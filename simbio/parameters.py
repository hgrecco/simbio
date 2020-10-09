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


class Parameter(BaseParameter):
    pass
