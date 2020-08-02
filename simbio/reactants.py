"""
    simbio.reactants
    ~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .core import Content


class Reactant(Content):
    concentration: float = 0

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("Only floats and ints can multiply a Reactant.")

        return InReactionReactant(self, other)

    __rmul__ = __mul__


@dataclass(frozen=True)
class InReactionReactant:
    reactant: Reactant
    st_number: Union[int, float] = 1

    @property
    def name(self):
        return self.reactant.name

    @property
    def concentration(self):
        return self.reactant.concentration
