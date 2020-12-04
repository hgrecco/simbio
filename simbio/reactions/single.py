"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..components import Parameter, ReactionBalance, Species
from .core import SingleReaction


@dataclass
class Creation(SingleReaction):
    """A substance is created from nothing.

    ∅ -> A
    """

    A: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return None >> self.A

    @staticmethod
    def reaction_rate(t, rate):
        return rate

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ \varnothing ->[$rate] $A }")


@dataclass
class ExponentialCreation(SingleReaction):
    """A substance is created proportional to its abundance.

    A -> 2A
    """

    A: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return self.A >> 2 * self.A

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A


@dataclass
class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A -> ∅
    """

    A: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return self.A >> None

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] \varnothing }")


@dataclass
class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    A: Species
    B: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return self.A >> self.B

    @staticmethod
    def reaction_rate(t, A, rate):
        return rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] $B }")


@dataclass
class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    A: Species
    B: Species
    AB: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return self.A + self.B >> self.AB

    @staticmethod
    def reaction_rate(t, A, B, rate):
        return rate * A * B

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $B ->[$rate] $AB }")


@dataclass
class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    AB: Species
    A: Species
    B: Species
    rate: Parameter

    def reaction_balance(self) -> ReactionBalance:
        return self.AB >> self.A + self.B

    @staticmethod
    def reaction_rate(t, AB, rate):
        return rate * AB

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB ->[$rate] $A + $B }")


# class SingleReplacement(SingleReaction):
#     """A single uncombined element replaces another in a compound.
#
#     A + BC -> AC + B
#     """


# class DoubleReplacement(SingleReaction):
#     """The anions and cations of two compounds switch places and form two entirely different compounds.
#
#     AB + CD -> AD + CB
#     """
