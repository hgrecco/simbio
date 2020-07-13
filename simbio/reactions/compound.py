"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from typing import Tuple

from ..parameters import Parameter
from ..reactants import InReactionReactant, Reactant
from .core import BaseReaction
from .single import Dissociation, Synthesis


class CompoundReaction(BaseReaction):
    """Base class for all compound reactions, which can be written as
    combination of others.
    """

    _reactions: Tuple[BaseReaction, ...]

    def __init__(self, **kwargs):
        self._reactant_names = []
        self._parameter_names = []
        self.st_numbers = []

        for key, value in kwargs.items():
            if isinstance(value, InReactionReactant):
                self.st_numbers.append(value.st_number)
                value = value.reactant
                self._reactant_names.append(key)
            elif isinstance(value, Reactant):
                self.st_numbers.append(1)
                self._reactant_names.append(key)
            elif isinstance(value, Parameter):
                self._parameter_names.append(key)
            else:
                raise TypeError(f"{value} is not a Reactant or Parameter.")
            setattr(self, key, value)

        for name in ("_reactant_names", "_parameter_names", "st_numbers"):
            setattr(self, name, tuple(getattr(self, name)))

    def yield_ip_rhs(self, global_reactants=None, global_parameters=None):
        for reaction in self._reactions:
            yield from reaction.yield_ip_rhs(global_reactants, global_parameters)

    def yield_latex_equations(self, *, use_brackets=True):
        for reaction in self._reactions:
            yield reaction.yield_latex_equations(use_brackets=use_brackets)

    def yield_latex_reaction(self):
        for reaction in self._reactions:
            yield reaction.yield_latex_reaction()

    def yield_latex_reactant_values(self):
        for reaction in self._reactions:
            yield from reaction.yield_latex_reactant_values()

    def yield_latex_parameter_values(self):
        for reaction in self._reactions:
            yield from reaction.yield_latex_parameter_values()


class ReversibleSynthesis(CompoundReaction):
    """A Synthesis and Dissociation reactions.

    A + B <-> AB
    """

    A: Reactant
    B: Reactant
    AB: Reactant

    forward_rate: float
    reverse_rate: float

    def __init__(self, *, A, B, AB, forward_rate, reverse_rate):
        super().__init__(
            A=A, B=B, AB=AB, forward_rate=forward_rate, reverse_rate=reverse_rate
        )
        self._reactions = (
            Synthesis(A=A, B=B, AB=AB, rate=forward_rate),
            Dissociation(A=A, B=B, AB=AB, rate=reverse_rate),
        )

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $A + $B <=>[$forward_rate][$reverse_rate] $AB"
        )
