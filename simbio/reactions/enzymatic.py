from dataclasses import dataclass

from ..parameters import Parameter
from ..species import Species
from .compound import CompoundReaction, Dissociation, ReversibleSynthesis
from .single import SingleReaction


class MichaelisMenten(CompoundReaction):
    E: Species
    S: Species
    ES: Species
    P: Species
    forward_rate: Parameter
    reverse_rate: Parameter
    catalytic_rate: Parameter

    def yield_reactions(self):
        yield ReversibleSynthesis(
            A=self.E,
            B=self.S,
            AB=self.ES,
            forward_rate=self.forward_rate,
            reverse_rate=self.reverse_rate,
        )
        yield Dissociation(AB=self.ES, A=self.E, B=self.P, rate=self.catalytic_rate)

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $E + $S <=>[$forward_rate][reverse_rate] $ES ->[$catalytic_rate] $P }"
        )

    def to_eq_approx(self):
        raise NotImplementedError
        # Should we generate a new S species or modify the concentration to add ES
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
        raise NotImplementedError
        # Should we generate a new S species or modify the concentration to add ES
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


@dataclass
class MichaelisMentenEqApprox(SingleReaction):
    S: Species
    P: Species
    maximum_velocity: Parameter
    dissociation_constant: Parameter

    @staticmethod
    def rhs(t, S, P, maximum_velocity, dissociation_constant):
        delta = maximum_velocity * S / (dissociation_constant + S)
        return -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $S ->[MMEq($maximum_velocity, $dissociation_constant)] $P }"
        )


@dataclass
class MichaelisMentenQuasiSSAprox(SingleReaction):
    S: Species
    P: Species
    maximum_velocity: Parameter
    michaelis_constant: Parameter

    @staticmethod
    def rhs(t, S, P, maximum_velocity, michaelis_constant):
        delta = maximum_velocity * S / (michaelis_constant + S)
        return -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(
            r"\ce{ $S ->[MMEq($maximum_velocity, $michaelis_constant)] $P }"
        )
