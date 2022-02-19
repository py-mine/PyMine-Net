"""
Contains a "strict" implementation of abc.ABC, as only Python 3.10+ actually enforces abc.ABC.

- Subclasses of abstract classes must implement all abstract methods/classmethods/staticmethods
- A method's typehints are also enforced, if abstract method a has a return annotation of MyClass,
    the implemented method must have a return annotation of MyClass or a subclass of MyClass.
"""

from typing import Optional, Tuple, Type

__all__ = ("abstract", "StrictABC")


class AbstractObjData:
    __slots__ = ("annotations",)

    def __init__(self, annotations: dict = None):
        self.annotations = annotations


def abstract(obj):
    obj.__abstract__ = AbstractObjData(getattr(obj, "__annotations__", None))
    return obj


def check_annotations(a: dict, b: dict) -> bool:
    for k, v in a.items():
        if k not in b:
            return False

        if type(v) is str:
            return type(b[k]) is str and v == b[k]

        if not issubclass(b[k], v):
            return False

    return True


class UnimplementedAbstractError(Exception):
    def __init__(self, cls_name: str, obj_name: str):
        super().__init__(f"Class {cls_name} didn't implement abstract {obj_name}.")


class MismatchedOverridenAbstractError(Exception):
    def __init__(
        self, cls_name: str, obj_name: str, abstract_annotations: dict, obj_annotations: dict
    ):
        super().__init__(
            f"Overriden abstract {obj_name} of {cls_name} has mismatched annotations: {obj_name}({self.fmt_annos(abstract_annotations)}) != {obj_name}({self.fmt_annos(obj_annotations)})."
        )

    @staticmethod
    def fmt_annos(dct: dict) -> str:
        return ",".join(f"{k}:{getattr(v, '__name__', str(v))}" for k, v in dct.items())


class StrictABCMeta(type):
    def __new__(cls, name: str, bases: Tuple[Type[object]], dct: dict):
        self = super().__new__(cls, name, bases, dct)

        # iterate through base classes
        for base in bases:
            # iterate through objects
            for obj_name in dir(base):
                obj = getattr(base, obj_name)

                abstract_data: Optional[AbstractObjData] = getattr(obj, "__abstract__", None)

                self_obj = getattr(self, obj_name, None)

                # check if it's an abstract object
                if abstract_data is not None:
                    # check to see if this class implements that abstract object
                    if hasattr(self_obj, "__abstract__"):
                        raise UnimplementedAbstractError(self.__name__, obj.__name__)

                    if type(self_obj) is not type(obj):
                        raise UnimplementedAbstractError(self.__name__, obj.__name__)

                    # check annotations if there are any
                    if abstract_data.annotations is not None:
                        self_obj_annotations = getattr(self_obj, "__annotations__", None)

                        if self_obj_annotations is None and abstract_data.annotations is not None:
                            raise MismatchedOverridenAbstractError(
                                self.__name__,
                                obj.__name__,
                                abstract_data.annotations,
                                self_obj_annotations,
                            )

                        if not check_annotations(abstract_data.annotations, self_obj_annotations):
                            raise MismatchedOverridenAbstractError(
                                self.__name__,
                                obj.__name__,
                                abstract_data.annotations,
                                self_obj_annotations,
                            )

        return self


class StrictABC(metaclass=StrictABCMeta):
    pass


# Example:
# class AbstractTest(StrictABC):
#     def __init__(self, something):
#         self.something = something

# class AbstractTest2(AbstractTest):
#     @abstract
#     def my_abstract_method(self, a: str):
#         print("in abstract method")

#     @classmethod
#     @abstract
#     def my_abstract_classmethod(self, a: str):
#         print("in abstract classmethod")

# class Test(AbstractTest2):
#     def my_abstract_method(self, a: str):
#         print("in method")

#     @classmethod
#     def my_abstract_classmethod(self, a: str):
#         print("in classmethod")
