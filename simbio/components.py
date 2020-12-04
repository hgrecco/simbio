from __future__ import annotations

from collections import UserDict, defaultdict
from dataclasses import dataclass
from itertools import chain
from numbers import Real

from .core import Content


class Component(Content):
    value: float

    def __init__(self, value, *, name=None, override=False):
        if value < 0:
            raise ValueError(f"The value of {self} must be positive.")
        self.value = value
        self.override = override
        super().__init__(name=name)

    def copy(self):
        return self.__class__(self.value, name=self.name)

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    def __eq__(self, other):
        """Components are equal if they have the same name, value and
        are located in the same place relative to their corresponding
        root Compartments."""
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.value == other.value) and (
            self._relative_name_from_root() == other._relative_name_from_root()
        )

    def __repr__(self):
        return self.name


class Parameter(Component):
    pass


class Species(Component):
    def __mul__(self, other):
        if not isinstance(other, Real):
            raise TypeError("Only numbers can multiply a Species.")

        return InReactionSpecies({self: other})

    __rmul__ = __mul__

    def __and__(self, other):
        """A & B creates a new species, representing the binding of A and B,
        which is added to the first common parent compartment of A and B.
        The new species name is constructed by joining the names of A and B with
        underscores."""

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


class InReactionSpecies(UserDict):
    """A dictionary of species and their stoichiometric number.

    Adding InReactionSpecies or multiplying by a number creates
    a new instance of InReactionSpecies.

    >>> A, B = Species(0, name="A"), Species(0, name="B")
    >>> 2 * A + 3 * B
    InReactionSpecies({A: 2, B: 3})

    Right-shifting InReactionSpecies creates a ReactionBalance.
    >>> A = Species(0, name="A")
    >>> 2 * A >> 3 * A
    ReactionBalance(reactants={A: 2}, products={A: 3})
    """

    @staticmethod
    def _check_number(number):
        if not isinstance(number, Real):
            raise TypeError(f"Must be a real number, not {number}")

        if number <= 0:
            raise ValueError("Must be a positive number.")

    def __setitem__(self, species: Species, st_number: float) -> None:
        self._check_number(st_number)
        if species in self.data:
            self.data[species] += st_number
        else:
            super().__setitem__(species, st_number)

    def __add__(self, other):
        if other.__class__ is not self.__class__:
            raise TypeError
        new = self.copy()
        new.update(other)
        return new

    __radd__ = __add__

    def __mul__(self, other):
        self._check_number(other)
        return self.__class__({species: other * st for species, st in self.items()})

    __rmul__ = __mul__

    def __rshift__(self, other):
        if other is None:
            return ReactionBalance(self, {})
        elif other.__class__ is self.__class__:
            return ReactionBalance(self, other)
        else:
            raise TypeError(f"{other} is neither an InReactionSpecies nor None.")

    def __rrshift__(self, other):
        if other is None:
            return ReactionBalance({}, self)
        return NotImplemented

    def __repr__(self):
        return " + ".join(f"{st} {name}" for name, st in self.items())


@dataclass
class ReactionBalance:
    """A ReactionBalance identifies an equivalence class of reactions.

    It has two instances of InReactionsSpecies for reactants and products.
    Two reactions are equivalent if their reactants and products are the same,
    that is, they involve the same species with the same stoichoimetric numbers.

    Right-shifting InReactionSpecies creates a ReactionBalance.
    >>> A = Species(0, name="A")
    >>> 2 * A >> 3 * A
    ReactionBalance(reactants={A: 2}, products={A: 3})
    """

    reactants: InReactionSpecies
    products: InReactionSpecies

    @property
    def change(self):
        """A dictionary of species and their change in number
        (creation or destruction) in the corresponding reaction."""
        out = defaultdict(float)
        for species, st_number in self.reactants.items():
            out[species] -= st_number
        for species, st_number in self.products.items():
            out[species] += st_number
        return out

    def __hash__(self) -> int:
        return sum(map(hash, chain(self.reactants, self.products)))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.reactants == other.reactants) and (self.products == other.products)

    def __repr__(self):
        return f"{repr(self.reactants)} >> {repr(self.products)}"
