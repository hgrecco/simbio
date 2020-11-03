"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..components import Parameter, Species
from .core import Reaction
from .single import Conversion, Dissociation, Synthesis


@dataclass
class ReversibleSynthesis(Reaction):
    """A Synthesis and Dissociation reactions.

    A + B <-> AB
    """

    A: Species
    B: Species
    AB: Species
    forward_rate: Parameter
    reverse_rate: Parameter

    def reactions(self):
        yield Synthesis(A=self.A, B=self.B, AB=self.AB, rate=self.forward_rate)
        yield Dissociation(AB=self.AB, A=self.A, B=self.B, rate=self.reverse_rate)

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $A + $B <=>[$forward_rate][$reverse_rate] $AB"
        )


@dataclass
class Equilibration(Reaction):
    """A forward and backward Conversion reactions.

    A <-> B
    """

    A: Species
    B: Species
    forward_rate: Parameter
    reverse_rate: Parameter

    def reactions(self):
        yield Conversion(A=self.A, B=self.B, rate=self.forward_rate)
        yield Conversion(A=self.B, B=self.A, rate=self.reverse_rate)


@dataclass
class CatalyzeConvert(Reaction):
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

    def reactions(self):
        yield ReversibleSynthesis(
            A=self.A,
            B=self.B,
            AB=self.AB,
            forward_rate=self.forward_rate,
            reverse_rate=self.reverse_rate,
        )
        yield Conversion(A=self.AB, B=self.P, rate=self.conversion_rate)
