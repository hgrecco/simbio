from ..components import Parameter, ReactionGroup, SingleReaction, Species
from .compound import Dissociation, ReversibleSynthesis


class MichaelisMenten(ReactionGroup):
    E: Species
    S: Species
    ES: Species
    P: Species
    forward_rate: Parameter
    reverse_rate: Parameter
    catalytic_rate: Parameter

    binding_reaction = ReversibleSynthesis(
        A=E,  # noqa: F821
        B=S,  # noqa: F821
        AB=ES,  # noqa: F821
        forward_rate=forward_rate,  # noqa: F821
        reverse_rate=reverse_rate,  # noqa: F821
    )
    dissociation_reaction = Dissociation(
        AB=ES,  # noqa: F821
        A=E,  # noqa: F821
        B=P,  # noqa: F821
        rate=catalytic_rate,  # noqa: F821
    )

    def to_eq_approx(self):
        raise NotImplementedError
        # Should we generate a new S species or modify the concentration to add ES
        # Should we invalidate this reaction (self) because we are using these elsewhere
        # michaelis_constant = reverse_rate / forward_rate
        # return MichaelisMentenEqApprox(
        #     S=S,
        #     P=P,
        #     maximum_velocity=catalytic_rate * (E.concentration + ES.concentration),
        #     michaelis_constant=michaelis_constant,
        # )

    def to_qss_approx(self):
        raise NotImplementedError
        # Should we generate a new S species or modify the concentration to add ES
        # Should we invalidate this reaction (self) because we are using these elsewhere
        # michaelis_constant = (reverse_rate + catalytic_rate) / forward_rate
        # return MichaelisMentenEqApprox(
        #     S=S,
        #     P=P,
        #     maximum_velocity=catalytic_rate * (E.concentration + ES.concentration),
        #     michaelis_constant=michaelis_constant,
        # )


class MichaelisMentenEqApprox(SingleReaction):
    S: Species
    P: Species
    maximum_velocity: Parameter
    dissociation_constant: Parameter

    @property
    def reactants(self):
        return (self.S,)

    @property
    def products(self):
        return (self.P,)

    @staticmethod
    def reaction_rate(t, S, maximum_velocity, dissociation_constant):
        return maximum_velocity * S / (dissociation_constant + S)


class MichaelisMentenQuasiSSAprox(SingleReaction):
    S: Species
    P: Species
    maximum_velocity: Parameter
    michaelis_constant: Parameter

    @property
    def reactants(self):
        return (self.S,)

    @property
    def products(self):
        return (self.P,)

    @staticmethod
    def reaction_rate(t, S, maximum_velocity, michaelis_constant):
        return maximum_velocity * S / (michaelis_constant + S)
