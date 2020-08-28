"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from inspect import signature
from typing import Tuple

from ..parameters import Parameter
from ..species import Species
from .core import BaseReaction
from .single import Dissociation, Synthesis


class CompoundReaction(BaseReaction):
    """Base class for all compound reactions, which can be written as
    combination of others.
    """

    reactions: Tuple[BaseReaction, ...] = field(init=False)

    def __init_subclass__(cls):
        super().__init_subclass__()

        sig = signature(cls.yield_reactions)
        if len(sig.parameters) != 1:
            raise ValueError(
                f"{cls.__qualname__}.yield_reactions should have no parameters."
            )

    def __post_init__(self):
        """Generates and saves the reactions from yield_reactions."""
        self.reactions = tuple(self.yield_reactions())
        # super().__post_init__() must be called after collecting species and
        # parameters, and generating reactions, as it will unpack InReactionSpecies.
        super().__post_init__()

    def yield_reactions(self):
        raise NotImplementedError

    def _yield_ip_rhs(self, global_species=None, global_parameters=None):
        for reaction in self.reactions:
            yield from reaction._yield_ip_rhs(global_species, global_parameters)

    def yield_latex_equations(self, *, use_brackets=True):
        for reaction in self.reactions:
            yield reaction.yield_latex_equations(use_brackets=use_brackets)

    def yield_latex_reaction(self):
        for reaction in self.reactions:
            yield reaction.yield_latex_reaction()

    def yield_latex_species_values(self):
        for reaction in self.reactions:
            yield from reaction.yield_latex_species_values()

    def yield_latex_parameter_values(self):
        for reaction in self.reactions:
            yield from reaction.yield_latex_parameter_values()


@dataclass
class ReversibleSynthesis(CompoundReaction):
    """A Synthesis and Dissociation reactions.

    A + B <-> AB
    """

    A: Species
    B: Species
    AB: Species
    forward_rate: Parameter
    reverse_rate: Parameter

    def yield_reactions(self):
        yield Synthesis(A=self.A, B=self.B, AB=self.AB, rate=self.forward_rate)
        yield Dissociation(AB=self.AB, A=self.A, B=self.B, rate=self.reverse_rate)

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $A + $B <=>[$forward_rate][$reverse_rate] $AB"
        )
