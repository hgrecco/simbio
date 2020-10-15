from __future__ import annotations

from .core import Content


class BaseParameter(Content):
    value: float

    def __init__(self, value, *, name=None, override=False):
        self.value = value
        self.override = override
        super().__init__(name=name)

    def copy(self):
        return self.__class__(self.value, name=self.name)

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name == other.name) and (self.value == other.value)


class Parameter(BaseParameter):
    pass
