from abc import abstractmethod
from unittest.mock import Mock

import pytest

from pymine_net.strict_abc import StrictABC, is_abstract, optionalabstractmethod


class Helpers:
    @abstractmethod
    def helper_ab_func(self, x):
        ...

    @optionalabstractmethod
    def helper_optional_ab_func(self, x):
        ...

    def helper_func(self, x):
        return x

    @abstractmethod
    def helper_annotated_ab_func(self, x: int, y: int) -> int:
        ...

    @optionalabstractmethod
    def helper_annotated_optional_ab_func(self, x: int, y: int) -> int:
        ...

    def helper_annotated_func(self, x: int, y: int) -> int:
        return x + y

    def helper_unannoteated_func(self, x, y):
        return x + y


def test_abc_creation():
    test_cls = type(
        "TestAbstract",
        (StrictABC,),
        {
            "func": Helpers.helper_func,
            "ab_func": Helpers.helper_ab_func,
            "optional_ab_func": Helpers.helper_optional_ab_func,
        },
    )

    cases = [
        ("func", {"optional_ab": False, "ab": False}),
        ("ab_func", {"optional_ab": False, "ab": True}),
        ("optional_ab_func", {"optional_ab": True, "ab": False}),
    ]

    for method_name, params in cases:
        # Make sure the class was properly made with the function
        assert hasattr(test_cls, method_name)
        fun = getattr(test_cls, method_name)
        # Make sure there's no decorator failure and the function is still callable
        assert callable(fun)
        # Make sure the function is following the expected params
        assert getattr(fun, "__isabstractmethod__", False) is params["ab"]
        assert getattr(fun, "__isoptionalabstractmethod__", False) is params["optional_ab"]

    # Make sure the class has __abstractmethods__ list, which only holds
    # the true abstractmethods (not optional abstractmethods)
    assert hasattr(test_cls, "__abstractmethods__")
    abstract_methods = getattr(test_cls, "__abstractmethods__")
    assert "ab_func" in abstract_methods
    assert "optional_ab_func" not in abstract_methods


def test_abc_definition_enforcement():
    test_cls = type("TestAbstract", (StrictABC,), {"foo": Helpers.helper_ab_func})

    # Fail for class without overridden definition
    with pytest.raises(TypeError):
        type("Test", (test_cls,), {})

    # Succeed for class with overridden definition
    type("Test", (test_cls,), {"foo": Helpers.helper_func})

    # Succeed for class without overridden definition, with ignored definition check
    type("ExtendedTestAbstract", (test_cls,), {}, definition_check=False)


def test_abc_no_optional_definition_enforcement():
    test_cls = type("TestAbstract", (StrictABC,), {"foo": Helpers.helper_optional_ab_func})

    # Should succeed, even without providing a definition of the optional abstract function
    type("Test", (test_cls,), {})

    # Should succeed with overridden optional abstract function with valid function
    type("Test", (test_cls,), {"foo": Helpers.helper_func})


def test_abc_typing_enforcement():
    test_cls = type("TestAbstract", (StrictABC,), {"foo": Helpers.helper_annotated_ab_func})

    # Fail for class without matching type annotated overridden method
    with pytest.raises(TypeError):
        type("Test", (test_cls,), {"foo": Helpers.helper_unannoteated_func})

    # Succeed for class with matching type annotated overridden method
    type("Test", (test_cls,), {"foo": Helpers.helper_annotated_func})

    # Succeed for class wtthout matching type annotated overridden method, but without type-check enabled
    type("Test", (test_cls,), {"foo": Helpers.helper_unannoteated_func}, typing_check=False)

    # Succeed for unoverridden method (without definition check)
    type("Test", (test_cls,), {}, definition_check=False)


def test_abc_optional_typing_enforcement():
    test_cls = type(
        "TestAbstract", (StrictABC,), {"foo": Helpers.helper_annotated_optional_ab_func}
    )

    # Succeed for unoverridden method (without definition check)
    type("Test", (test_cls,), {}, definition_check=False)

    # Succeed for class with matching type annotated overridden method
    type("Test", (test_cls,), {"foo": Helpers.helper_annotated_func})

    # Fail for class without matching type annotated overridden maethod
    with pytest.raises(TypeError):
        type("Test", (test_cls,), {"foo": Helpers.helper_unannoteated_func})


def test_is_abstract():
    # is_abstract check should obviously pass for an abstract method
    assert is_abstract(Helpers.helper_ab_func) is True
    # is_abstract check should also pass for optional abstract methods
    assert is_abstract(Helpers.helper_optional_ab_func) is True
    # is_abstract check should not pass for a regular method
    assert is_abstract(Helpers.helper_func) is False


def test_forward_annotation_comparison():
    compare = lambda x, y: StrictABC._compare_forward_reference_annotations(x, y, Mock())[0]

    # We should succeed for exactly same forward reference strings
    assert compare("Foo", "Foo") is True

    # We should also succeed for unqualified comparison for reference strings
    assert compare("py_mine.xyz.Foo", "Foo") is True
    assert compare("Foo", "py_mine.zyx.Foo") is True

    # We should fail if the strings are completely different
    assert compare("Foo", "Bar") is False

    Foo = type("Foo", (), {})
    # We should succeed for comparing string "Foo" and real Foo named class
    assert compare(Foo, "Foo") is True
    assert compare("Foo", Foo) is True

    Bar = type("Bar", (), {})
    # We should fail for comparing string "Foo" and real Bar named class
    assert compare(Bar, "Foo") is False
    assert compare("Foo", Bar) is False
