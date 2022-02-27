"""
Contains a "strict" implementation of abc.ABC, enforcing presnce of all abstract methods on class creation.

- Subclasses of abstract classes must implement all abstract methods/classmethods/staticmethods
- A method's typehints are also enforced, if abstract method a has a return annotation of MyClass,
    the implemented method must have a return annotation of MyClass or a subclass of MyClass.
"""
from __future__ import annotations

import inspect
from abc import ABCMeta
from typing import TYPE_CHECKING, Callable, List, Tuple, Type, Union, cast, overload

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ("StrictABC", "optionalabstractmethod", "is_abstract")


def optionalabstractmethod(funcobj: Callable) -> Callable:
    """Marks given function as an optional abstract method.

    This means it's presnce won't be required, but if it will be present, we can
    run the typing checks provided by the strict ABC.

    NOTE: This will get removed along with the entire type-enforcement system eventually.
    """
    funcobj.__isoptionalabstractmethod__ = True
    return funcobj


def is_abstract(funcobj: Callable) -> bool:
    """Checks whether a given function is an abstract function."""
    return getattr(funcobj, "__isabstractmethod__", False) or getattr(
        funcobj, "__isoptionalabstractmethod__", False
    )


class StrictABCMeta(ABCMeta):
    """Strict extension of abc.ABCMeta, enforcing abstract methods on definitions and typing checks.

    Regular abc.ABCMeta only enforces abstract methods to be present on class initialization,
    however, this often isn't enough, because we usually want to get runtime errors immediately,
    whenever a class  would be defined without implementing all of the abstract methods. With
    behavior like this, we can ensure that we encounter a runtime failure before this behavior ever
    gets a chance of affecting things, this is especially important for static and class methods which
    don't need initialization to be called.

    This class also introduces typing checks, which require the overridden methods to follow the
    type-hints specified in the initial abstract methods. This prevents bad unexpected behavior,
    and it enforces clean type checkable code."""

    def __new__(
        mcls,
        name: str,
        bases: Tuple[Type[object], ...],
        dct: dict[str, object],
        definition_check: bool = True,
        typing_check: bool = True,
    ):
        cls = super().__new__(mcls, name, bases, dct)

        # Find all abstract methods and optional abstract methods which are still present and weren't overridden
        # excluding those defined in this class directly, since if a class defines new abstract method in it,
        # we obviously don't expect it to be implemented in that class.
        ab_methods = {
            method_name
            for method_name in cls.__abstractmethods__
            if method_name not in cls.__dict__
        }
        optional_ab_methods = {
            method_name
            for method_name in dir(cls)
            if getattr(getattr(cls, method_name), "__isoptionalabstractmethod__", False)
            and method_name not in cls.__dict__
        }

        if definition_check and len(ab_methods) > 0:
            missing_methods_str = ", ".join(ab_methods)
            if len(optional_ab_methods) > 0:
                missing_methods_str += ", and optionally also: " + ", ".join(optional_ab_methods)
            raise TypeError(
                f"Can't define class '{name}' with unimplemented abstract methods: {missing_methods_str}."
            )
        if typing_check:
            abc_classes = []
            for base_cls in bases:
                if isinstance(base_cls, mcls) and base_cls not in {mcls, cls}:
                    abc_classes.append(base_cls)

            mcls._check_annotations(cls, abc_classes)

        return cls

    @classmethod
    def _check_annotations(mcls, cls: Self, abc_classes: List[Self]) -> None:
        """Make sure all overridden methods in the class match the original definitions in ABCs.

        This works by finding every abstract method in the ABC classes (present in the classe's MRO),
        getting their type annotations and comparing them with the annotations in the overridden methods.

        If an abstract method definition is found, but overridden implementation in the class isn't present,
        this method will be skipped."""
        # Get all of the defined abstract methods in the ABCs
        ab_methods = []
        for abc_cls in abc_classes:
            for ab_method_name in abc_cls.__abstractmethods__:
                ab_method = getattr(abc_cls, ab_method_name)
                if not callable(ab_method):
                    raise TypeError(
                        f"Expected '{ab_method_name}' to be an abstractmethod, but it isn't callable."
                    )
                ab_methods.append((ab_method_name, ab_method))

            # This code is incredibely inefficient and I hate it, it's only here
            # because I was forced to implement support for optional abstract methods
            # which should never have been a thing, oh well...
            for obj_name in dir(abc_cls):
                obj_value = getattr(abc_cls, obj_name)
                if getattr(obj_value, "__isoptionalabstractmethod__", False):
                    if not callable(obj_value):
                        raise TypeError(
                            f"Expected '{obj_name}' to be an optional abstractmethod, but it isn't callable."
                        )
                    ab_methods.append((obj_name, obj_value))

        # Get matching overridden methods in the class, to the collected abstract methods
        _MISSING_SENTINEL = object()
        for ab_method_name, ab_method in ab_methods:
            defined_method = getattr(cls, ab_method_name, _MISSING_SENTINEL)

            if defined_method is _MISSING_SENTINEL:
                continue  # Skip unoverridden abstract methods

            if not callable(defined_method):
                raise TypeError(
                    f"Expected '{ab_method_name}' to be an abstractmethod, but it isn't callable."
                )

            # Compare the annotations
            mcls._compare_annotations(ab_method, defined_method, ab_method_name)

    @classmethod
    def _compare_annotations(
        mcls,
        expected_f: Callable,
        compare_f: Callable,
        method_name: str,
    ) -> None:
        """Compare annotations between two given functions.

        - If the first (expected) function doesn't have any annotations, this check is skipped.
        - If the second (compare) function doesn't have any annotations, check fails (TypeError).
        - If the second (compare) function's signature isn't compatible the expected signature, check fails (TypeError).
        - Otherwise, if the signatures are compatible, the check is passed (returns None).

        NOTE: This check works, but it's not at all reliable, and it's behavior with forward references is very much
        incomplete and inaccurate, and it will never be accurate, because doing type-enforcing on runtime like this
        simply isn't something that the python's typing system was designed for, types should be ensured with a proper
        type-checker, not with runtime checks. This also completely lacks support for subtypes which don't pass issubclass
        check, such as protocols. And support for string forward annotations is hacky at best.

        This function is only here temporarily, until a type-checker is added which will replace this.
        """
        try:
            expected_ann = inspect.get_annotations(expected_f, eval_str=True)
        except NameError:
            expected_ann = inspect.get_annotations(expected_f)
        try:
            compare_ann = inspect.get_annotations(compare_f, eval_str=True)
        except NameError:
            compare_ann = inspect.get_annotations(compare_f)

        err_msg = f"Mismatched annotations in '{method_name}'."

        if len(expected_ann) == 0:  # Nothing to compare
            return

        if len(compare_ann) == 0:
            raise TypeError(
                err_msg
                + f" Compare method has no annotations, but some were expected ({expected_ann})."
            )

        for key, exp_val in expected_ann.items():
            if key not in compare_ann:
                raise TypeError(
                    err_msg + f" Annotation for '{key}' not present, should be {exp_val}."
                )

            cmp_val = compare_ann[key]

            # In case we weren't able to evaluate the string forward reference annotations
            # we can at least check if the string they hold is the same. This isn't ideal,
            # and can cause issues, and incorrect failures, but it's the best we can do.
            if isinstance(cmp_val, str) or isinstance(exp_val, str):
                return mcls._compare_forward_reference_annotations(exp_val, cmp_val, err_msg, key)

            try:
                if not issubclass(cmp_val, exp_val):
                    raise TypeError(
                        err_msg
                        + f" Annotation for '{key}' isn't compatible, should be {exp_val}, got {cmp_val}."
                    )
            except TypeError:
                # This can happen when cmp_val isn't a class, for example with it set to `None`
                # Do a literal 'is' comparison here when that happens
                if cmp_val is not exp_val:
                    raise TypeError(
                        err_msg
                        + f" Annotation for '{key}' isn't compatible, should be {exp_val}, got {cmp_val}."
                    )

    @overload
    @staticmethod
    def _compare_forward_reference_annotations(
        exp_val: str, cmp_val: object, err_msg: str, key: str
    ):
        ...

    @overload
    @staticmethod
    def _compare_forward_reference_annotations(
        exp_val: object, cmp_val: str, err_msg: str, key: str
    ):
        ...

    @overload
    @staticmethod
    def _compare_forward_reference_annotations(exp_val: str, cmp_val: str, err_msg: str, key: str):
        ...

    @staticmethod
    def _compare_forward_reference_annotations(
        exp_val: Union[str, object],
        cmp_val: Union[str, object],
        err_msg: str,
        key: str,
    ):
        """This compares 2 annotations, out of which at least one is a string.

        This comparison isn't perfect and can result in succeeding for types which aren't
        actually matching type-wise, but they have the same string names. It can also fail
        to succeed for types which should in fact be matching. This can happen if the true
        types of those annotations weren't the same class, but rather a superclass and class,
        comparisons like these are impossible to resolve when we only know the string names.

        This method is temporary and will be removed, along with the entire type-checking
        functionality of the StrictABCMeta once a type-checker is in place.
        """
        compare_checks: List[Tuple[str, str]] = []
        if isinstance(cmp_val, str) and isinstance(exp_val, str):
            # When both objects are string forward reference annotations,
            # all we can do is try and compare these strings exactly
            compare_checks.append((cmp_val, exp_val))
        else:
            real: object = cmp_val if isinstance(exp_val, str) else exp_val
            fwd: str = exp_val if isinstance(exp_val, str) else cast(str, cmp_val)

            # If we have a forward reference and an object to compare between each other,
            # try to use multiple ways of converting the real object into a string and
            # and store all of these for any comparison later
            if hasattr(real, "__name__"):
                compare_checks.append((fwd, getattr(real, "__name__")))
            if hasattr(exp_val, "__qualname__"):
                compare_checks.append((fwd, getattr(real, "__qualname__")))

            # There's no point in continuing if we haven't found any way to convert
            # the real object into a string.
            if len(compare_checks) == 0:
                raise TypeError(
                    err_msg
                    + f" Can't compare annotations for '{key}', unable to convert a real object to a string"
                    f" for comparison against a string forward reference annotation. {real!r} ?= {fwd!r}"
                )

        # Also try to get the "unqualified names" and if comparing those succeed,
        # we assume a success too. This works by only taking the last part of the
        # string split by dots. So for example from 'py_mine.strict_abc.ABCMeta',
        # we'd just get 'ABCMeta'.
        for opt1, opt2 in compare_checks.copy():
            opt1_unqual = opt1.rsplit(".", maxsplit=1)[-1]
            opt2_unqual = opt2.rsplit(".", maxsplit=1)[-1]
            compare_checks.append((opt1_unqual, opt2_unqual))

        # Check if any of the options in our compare checks succeeds, if it does,
        # we consider the annotations to be the same and mark the type check as passing.
        # Even though this usually covers most cases, it doesn't mean we're 100% certain
        # about this. It's possible that the same type was imported under a different name,
        # or that we received a forward reference for a protocol type, which is a valid
        # supertype of the compare value, but we weren't able to resolve that.
        for opt1, opt2 in compare_checks:
            if opt1 == opt2:
                return

        raise TypeError(
            err_msg
            + f" String forward reference annotations for '{key}' don't match ({exp_val!r} != {cmp_val!r})"
        )


class StrictABC(metaclass=StrictABCMeta):
    """Strict implementation of abc.ABC, including definition time checks and typing checks.

    Example:
    >>> class AbstractTest(StrinctABC):
    ...     @abstractmethod
    ...     def foo(self, x: int) -> int:
    ...         pass
    >>> class Test(AbstractTest):
    ...     def foo(self, x: int) -> int
    ...         return 2 + x
    >>> class NotTest(AbstractTest):
    ...     def bar(self, x: int) -> int:
    ...         return 5 + x
    TypeError: Can't define class 'NotTest' with unimplemented abstract methods: foo.
    >>> class NotTest2(AbstractTest):
    ...     def foo(self, x: str) -> str:
    ...         return "hi " + x
    TypeError: Mismatched annotations in 'foo'. Annotation for 'x' isn't compatible, should be int, got str.
    >>> class ExtendedAbstractTest(StrictABC, definition_check=False):
    ...     @classmethod
    ...     @abstractmethod
    ...     def bar(cls, x: str) -> str:
    ...         pass
    >>> # No issues here

    For more info, check StrictABCMeta's doocstring."""

    __slots__ = ()
