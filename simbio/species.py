"""
    simbio.species
    ~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .parameters import BaseParameter


@dataclass(frozen=True, eq=False)
class Species(BaseParameter):
    value: float = 0

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("Only floats and ints can multiply a Species.")

        return InReactionSpecies(self, other)

    __rmul__ = __mul__


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
