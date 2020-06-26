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

    def __init__(self, *, E, S, ES, P, forward_rate, reverse_rate, catalytic_rate):
        super().__init__()
        self._reactions = (
            ReversibleSynthesis(
                A=E, B=S, AB=ES, forward_rate=forward_rate, reverse_rate=reverse_rate
            ),
            Dissociation(AB=ES, A=E, B=P, rate=catalytic_rate),
        )

    def to_eq_approx(self):
        # Should we generate a new S reactant or modify the concentration to add ES
        # Should we invalidate this reaction (self) because we are using these elsewhere
        michaelis_constant = self.reverse_rate / self.forward_rate
        return MichaelisMentenEqApprox(
            S=self.S,
            P=self.P,
            maximum_velocity=self.catalytic_rate
            * (self.E.concentration + self.ES.concentration),
            michaelis_constant=michaelis_constant,
        )

    def to_qss_approx(self):
        # Should we generate a new S reactant or modify the concentration to add ES
        # Should we invalidate this reaction (self) because we are using these elsewhere
        michaelis_constant = (
            self.reverse_rate + self.catalytic_rate
        ) / self.forward_rate
        return MichaelisMentenEqApprox(
            S=self.S,
            P=self.P,
            maximum_velocity=self.catalytic_rate
            * (self.E.concentration + self.ES.concentration),
            michaelis_constant=michaelis_constant,
        )


class MichaelisMentenEqApprox(SingleReaction):

    S: Reactant
    P: Reactant

    maximum_velocity: float
    dissociation_constante: float

    def _rhs(self, t, S, P):
        delta = self.maximum_velocity * S / (self.dissociation_constante + S)
        return -delta, delta


class MichaelisMentenQuasiSSAprox(SingleReaction):

    S: Reactant
    P: Reactant

    maximum_velocity: float
    michaelis_constant: float

    def _rhs(self, t, S, P):
        delta = self.maximum_velocity * S / (self.michaelis_constant + S)
        return -delta, delta
