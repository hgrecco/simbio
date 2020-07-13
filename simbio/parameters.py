from __future__ import annotations

from dataclasses import dataclass

from .core import Container, Content


@dataclass
class Parameter(Content):
    value: float = 0

    def __hash__(self):
        return id(self)

    def copy(self, name: str = None, belongs_to: Container = None) -> Parameter:
        return self.__class__(
            name=name or self.name, belongs_to=belongs_to, value=self.value,
        )
