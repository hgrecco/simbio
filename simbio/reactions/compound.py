"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from typing import Tuple

from simbio.reactants import Reactant

from .single import BaseReaction, Dissociation, Synthesis


class CompoundReaction(BaseReaction):
    """Base class for all compound reactions, which can be written as
    combination of others.
    """

    _reactions: Tuple[BaseReaction, ...]

    def names(self) -> Tuple[str, ...]:
        out = []
        for reaction in self._reactions:
            for name in reaction.names():
                if name not in out:
                    out.append(name)

        return tuple(out)

    def yield_ip_rhs(self, global_names=None):
        for reaction in self._reactions:
            yield from reaction.yield_ip_rhs(global_names)


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
        super().__init__()
        self._reactions = (
            Synthesis(A=A, B=B, AB=AB, rate=forward_rate),
            Dissociation(A=A, B=B, AB=AB, rate=reverse_rate),
        )
