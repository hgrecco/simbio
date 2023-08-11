"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from ..core import Compartment, Parameter, Species, assign, initial
from .single import Conversion, Dissociation, Synthesis


class ReversibleSynthesis(Compartment):
    """A Synthesis and Dissociation reactions.

    A + B <-> AB
    """

    A: Species = initial(default=0)
    B: Species = initial(default=0)
    AB: Species = initial(default=0)
    forward_rate: Parameter = assign(default=0)
    reverse_rate: Parameter = assign(default=0)

    forward_reaction = Synthesis(A=A, B=B, AB=AB, rate=forward_rate)
    backward_reaction = Dissociation(AB=AB, A=A, B=B, rate=reverse_rate)


class Equilibration(Compartment):
    """A forward and backward Conversion reactions.

    A <-> B
    """

    A: Species = initial(default=0)
    B: Species = initial(default=0)
    forward_rate: Parameter = assign(default=0)
    reverse_rate: Parameter = assign(default=0)

    forward_reaction = Conversion(A=A, B=B, rate=forward_rate)
    backward_reaction = Conversion(A=B, B=A, rate=reverse_rate)


class CatalyzeConvert(Compartment):
    """

    A + B <--> A:B --> P
    """

    A: Species = initial(default=0)
    B: Species = initial(default=0)
    AB: Species = initial(default=0)
    P: Species = initial(default=0)
    forward_rate: Parameter = assign(default=0)
    reverse_rate: Parameter = assign(default=0)
    conversion_rate: Parameter = assign(default=0)

    binding_reaction = ReversibleSynthesis(
        A=A, B=B, AB=AB, forward_rate=forward_rate, reverse_rate=reverse_rate
    )
    conversion_reaction = Conversion(A=AB, B=P, rate=conversion_rate)
