from __future__ import annotations

from ..components import Parameter, SingleReaction, Species


class Creation(SingleReaction):
    """A substance is created from nothing at a constant rate.

    ∅ -> A
    """

    A: Species
    rate: Parameter

    @property
    def reactants(self):
        return ()

    @property
    def products(self):
        return (self.A,)

    @staticmethod
    def reaction_rate(t, rate):
        return rate


class AutoCreation(SingleReaction):
    """A substance is created at a rate proportional to its abundance.

    A -> 2A
    """

    A: Species
    rate: Parameter

    @property
    def reactants(self):
        return (self.A,)

    @property
    def products(self):
        return (2 * self.A,)

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A


class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A -> ∅
    """

    A: Species
    rate: Parameter

    @property
    def reactants(self):
        return (self.A,)

    @property
    def products(self):
        return ()

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A


class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    A: Species
    B: Species
    rate: Parameter

    @property
    def reactants(self):
        return (self.A,)

    @property
    def products(self):
        return (self.B,)

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A


class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    A: Species
    B: Species
    AB: Species
    rate: Parameter

    @property
    def reactants(self):
        return (self.A, self.B)

    @property
    def products(self):
        return (self.AB,)

    @staticmethod
    def reaction_rate(t, A, B, rate):
        return rate * A * B


class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    AB: Species
    A: Species
    B: Species
    rate: Parameter

    @property
    def reactants(self):
        return (self.AB,)

    @property
    def products(self):
        return (self.A, self.B)

    @staticmethod
    def reaction_rate(t, AB, rate):
        return rate * AB
