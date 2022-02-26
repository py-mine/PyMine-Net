"""
Contains a "strict" implementation of abc.ABC, enforcing presnce of all abstract methods on class creation.

- Subclasses of abstract classes must implement all abstract methods/classmethods/staticmethods
- A method's typehints are also enforced, if abstract method a has a return annotation of MyClass,
    the implemented method must have a return annotation of MyClass or a subclass of MyClass.
"""
from __future__ import annotations

import inspect
from abc import ABCMeta
from typing import TYPE_CHECKING, Callable, List, Tuple, Type

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ("StrictABC", "optionalabstractmethod", "is_abstract")


def optionalabstractmethod(funcobj: Callable) -> Callable:
    """Marks given function as an optional abstract method.

    This means it's presnce won't be required, but if it will be present, we can
    run the typing checks provided by the strict ABC.

    NOTE: This will get removed along with the entire type-enforcement system eventually.
    """
    funcobj.__isabstractmethod__ = True  # Mimics abc.abstractmethod behavior
    funcobj.__isoptionalabstractmethod__ = True
    return funcobj


def is_abstract(funcobj: Callable) -> bool:
    """Checks whether a given function is an abstract function."""
    return getattr(funcobj, "__isabstractmethod__", False)


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
        ab_methods = {method_name for method_name in cls.__abstractmethods__ if method_name not in cls.__dict__}
        optional_ab_methods = {
            method_name for method_name in dir(cls)
            if getattr(getattr(cls, method_name), "__isoptionalabstractmethod__", False) and method_name not in cls.__dict__
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
        abc_methods = []
        for abc_cls in abc_classes:
            for abc_method_name in abc_cls.__abstractmethods__:
                abc_method = getattr(abc_cls, abc_method_name)
                if not callable(abc_method):
                    raise TypeError(
                        f"Expected '{abc_method_name}' to be an abstractmethod, but it isn't callable."
                    )
                abc_methods.append((abc_method_name, abc_method))

        # Get matching overridden methods in the class, to the collected abstract methods
        _MISSING_SENTINEL = object()
        for abc_method_name, abc_method in abc_methods:
            defined_method = getattr(cls, abc_method_name, _MISSING_SENTINEL)

            if defined_method is _MISSING_SENTINEL:
                continue  # Skip unoverridden abstract methods

            if not callable(defined_method):
                raise TypeError(
                    f"Expected '{abc_method_name}' to be an abstractmethod, but it isn't callable."
                )

            # Compare the annotations
            mcls._compare_annotations(abc_method, defined_method, abc_method_name)

    @staticmethod
    def _compare_annotations(expected_f: Callable, compare_f: Callable, method_name: str) -> None:
        """Compare annotations between two given functions.

        - If the first (expected) function doesn't have any annotations, this check is skipped.
        - If the second (compare) function doesn't have any annotations, check fails (TypeError).
        - If the second (compare) function's signature isn't compatible the expected signature, check fails (TypeError).
        - Otherwise, if the signatures are compatible, the check is passed (returns None).

        NOTE: This check works, but it's not at all reliable, and it's behavior with forward references is very much
        incomplete and inaccurate, and it will never be accurate, because doing type-enforcing on runtime like this
        simply isn't something that the python's typing system was designed for, types should be ensured with a proper
        type-checker, not with runtime checks. This also completely lacks support for subtypes which don't pass issubclass
        check, such as protocols. This is only here temporarily, until a type-checker is added which will replace this.
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
            if isinstance(exp_val, str):
                if not isinstance(cmp_val, str):
                    cmp_val = getattr(cmp_val, "__name__", None)
                    if cmp_val is None:
                        raise TypeError(
                            err_msg
                            + f" Can't compare annotations for '{key}', unable to evaluate the string forward reference"
                            f", and '__name__' of the compare function isn't available."
                        )
                if exp_val != cmp_val:
                    raise TypeError(
                        err_msg
                        + f" Forward reference annotations for '{key}' don't match ({exp_val!r} != {cmp_val!r})"
                    )

                # If we know the strings in the forward reference annotations are the same,
                # we can assume that they mean the same thing and mark the type check as passing,
                # however it doesn't mean we're 100% that it actually is the same type, but it's
                # the best we can do with unresolvable string annotations.
                return

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
                        + f" Annotation for '{key} isn't compatible, should be {exp_val}, got {cmp_val}."
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
