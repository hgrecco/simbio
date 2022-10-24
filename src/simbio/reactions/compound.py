"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from ..components.types import Parameter, ReactionGroup, Species
from .single import Conversion, Dissociation, Synthesis


class ReversibleSynthesis(ReactionGroup):
    """A Synthesis and Dissociation reactions.

    A + B <-> AB
    """

    A: Species
    B: Species
    AB: Species
    forward_rate: Parameter
    reverse_rate: Parameter

    forward_reaction = Synthesis(A=A, B=B, AB=AB, rate=forward_rate)
    backward_reaction = Dissociation(AB=AB, A=A, B=B, rate=reverse_rate)


class Equilibration(ReactionGroup):
    """A forward and backward Conversion reactions.

    A <-> B
    """

    A: Species
    B: Species
    forward_rate: Parameter
    reverse_rate: Parameter

    forward_reaction = Conversion(A=A, B=B, rate=forward_rate)
    backward_reaction = Conversion(A=B, B=A, rate=reverse_rate)


class CatalyzeConvert(ReactionGroup):
    """

    A + B <--> A:B --> P
    """

    A: Species
    B: Species
    AB: Species
    P: Species
    forward_rate: Parameter
    reverse_rate: Parameter
    conversion_rate: Parameter

    binding_reaction = ReversibleSynthesis(
        A=A, B=B, AB=AB, forward_rate=forward_rate, reverse_rate=reverse_rate
    )
    conversion_reaction = Conversion(A=AB, B=P, rate=conversion_rate)
