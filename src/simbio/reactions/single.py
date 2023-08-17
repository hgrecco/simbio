from __future__ import annotations

from ..core import Compartment, MassAction, Parameter, Species, assign, initial


class Creation(Compartment):
    """A substance is created from nothing at a constant rate.

    ∅ -> A
    """

    A: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[], products=[A], rate=rate)


class AutoCreation(Compartment):
    """A substance is created at a rate proportional to its abundance.

    A -> 2A
    """

    A: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[A], products=[2 * A], rate=rate)


class Destruction(Compartment):
    """A substance degrades into nothing.

    A -> ∅
    """

    A: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[A], products=[], rate=rate)


class Conversion(Compartment):
    """A substance convert to another.

    A -> B
    """

    A: Species = initial()
    B: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[A], products=[B], rate=rate)


class Synthesis(Compartment):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    A: Species = initial()
    B: Species = initial()
    AB: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[A, B], products=[AB], rate=rate)


class Dissociation(Compartment):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    AB: Species = initial()
    A: Species = initial()
    B: Species = initial()
    rate: Parameter = assign()
    reaction = MassAction(reactants=[AB], products=[A, B], rate=rate)
