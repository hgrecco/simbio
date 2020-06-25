from ..reactants import Reactant
from .compound import CompoundReaction, Dissociation, ReversibleSynthesis
from .single import SingleReaction


class MichaelisMenten(CompoundReaction):

    E: Reactant
    S: Reactant
    ES: Reactant
    P: Reactant

    forward_rate: float
    reverse_rate: float
    catalytic_rate: float

    def __init__(self, *, E, S, ES, P, forward_rate, reverse_rate, enzymatic_rate):
        super().__init__()
        self._reactions = (
            ReversibleSynthesis(
                A=E, B=S, AB=ES, forward_rate=forward_rate, reverse_rate=reverse_rate
            ),
            Dissociation(AB=ES, A=E, B=P, rate=enzymatic_rate),
        )


class MichaelisMentenReduced(SingleReaction):

    S: Reactant
    P: Reactant

    enzyme_concentration: float
    michaelis_constant: float
    catalytic_rate: float

    def _rhs(self, t, S, P):
        delta = (
            self.catalytic_rate
            * self.enzyme_concentration
            * S
            / (self.michaelis_constant + S)
        )
        return -delta, delta
