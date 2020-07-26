"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import inspect
from typing import Tuple, get_type_hints

from ..parameters import Parameter
from ..reactants import Reactant
from .core import BaseReaction, _check_signature
from .single import Dissociation, Synthesis


class CompoundReaction(BaseReaction):
    """Base class for all compound reactions, which can be written as
    combination of others.
    """

    _reactions: Tuple[BaseReaction, ...]

    def __init_subclass__(cls):
        """Initialize class from yield_reactions method.

        Check if yield_reactions method is well-defined. It must:
        - be a staticmethod
        - have an ordered signature (t, *Reactants, *Parameters)

        Continue class initialization with yield_reactions annotations in BaseReaction.
        """
        # Check if staticmethod
        if not isinstance(inspect.getattr_static(cls, "yield_reactions"), staticmethod):
            raise TypeError(
                f"{cls.__name__}.yield_reactions must be a staticmethod. Use @staticmethod decorator."
            )

        annotations = get_type_hints(cls.yield_reactions)
        cls.yield_reactions.__annotations__ = annotations
        _check_signature(cls.yield_reactions, t_first=False)
        return super().__init_subclass__(annotations=annotations)

    def __post_init__(self):
        """Generates and saves the reactions from yield_reactions."""
        reactants = dict(zip(self._reactant_names, self.reactants))
        parameters = dict(zip(self._parameter_names, self.parameters))
        self._reactions = tuple(self.yield_reactions(**reactants, **parameters))
        # super().__post_init__() must be called after collecting reactants and
        # parameters, and generating reactions, as it will unpack InReactionReactants.
        super().__post_init__()

    @staticmethod
    def yield_reactions(self, **kwargs):
        raise NotImplementedError

    def _yield_ip_rhs(self, global_reactants=None, global_parameters=None):
        for reaction in self._reactions:
            yield from reaction._yield_ip_rhs(global_reactants, global_parameters)

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

    @staticmethod
    def yield_reactions(
        A: Reactant,
        B: Reactant,
        AB: Reactant,
        forward_rate: Parameter,
        reverse_rate: Parameter,
    ):
        yield Synthesis(A=A, B=B, AB=AB, rate=forward_rate)
        yield Dissociation(A=A, B=B, AB=AB, rate=reverse_rate)

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $A + $B <=>[$forward_rate][$reverse_rate] $AB"
        )
