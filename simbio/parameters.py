from __future__ import annotations

from dataclasses import dataclass
from typing import Union

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
        return (
            self._relative_name_from_root() == other._relative_name_from_root()
        ) and (self.value == other.value)


class Parameter(BaseParameter):
    pass


class Species(BaseParameter):
    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("Only floats and ints can multiply a Species.")

        return InReactionSpecies(self, other)

    __rmul__ = __mul__

    def __and__(self, other):
        if not other.__class__ == self.__class__:
            return NotImplemented

        parent = self._common_parent(self, other)
        names = [parent._relative_name(s, sep="_") for s in (self, other)]
        name = "_".join(sorted(names))
        try:
            new = parent[name]
        except KeyError:
            new = self.__class__(0, name=name)
            parent._add(new)
        return new


@dataclass(frozen=True)
class InReactionSpecies:
    species: Species
    st_number: Union[int, float] = 1

    @property
    def name(self):
        return self.species.name

    @property
    def value(self):
        return self.species.value
