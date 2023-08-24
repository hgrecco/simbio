from typing import Any, TypeVar

T = TypeVar("T")


class Compartment:
    pass


class DynamicCompartment:
    def __init__(self, name: str):
        object.__setattr__(self, "compartment", type(name, (Compartment,), {}))

    def add(self, name: str, value: T) -> T:
        setattr(self, name, value)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        value.__set_name__(self.compartment, name)
        setattr(self.compartment, name, value)

    def __getattr__(self, name):
        try:
            return getattr(self.compartment, name)
        except AttributeError as e:
            e.add_note("component not found in Compartment")
            raise
