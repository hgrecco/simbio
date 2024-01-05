from ..core import Compartment, Parameter, RateLaw, Species, assign, initial
from .compound import Dissociation, ReversibleSynthesis


class MichaelisMenten(Compartment):
    E: Species = initial()
    S: Species = initial()
    ES: Species = initial()
    P: Species = initial()
    forward_rate: Parameter = assign()
    reverse_rate: Parameter = assign()
    catalytic_rate: Parameter = assign()

    binding_reaction = ReversibleSynthesis(
        A=E,
        B=S,
        AB=ES,
        forward_rate=forward_rate,
        reverse_rate=reverse_rate,
    )
    dissociation_reaction = Dissociation(
        AB=ES,
        A=E,
        B=P,
        rate=catalytic_rate,
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


class MichaelisMentenEqApprox(Compartment):
    S: Species = initial()
    P: Species = initial()
    maximum_velocity: Parameter = assign()
    dissociation_constant: Parameter = assign()
    reaction = RateLaw(
        reactants=[S],
        products=[P],
        rate_law=maximum_velocity * S / (dissociation_constant + S),
    )


class MichaelisMentenQuasiSSAprox(Compartment):
    S: Species = initial()
    P: Species = initial()
    maximum_velocity: Parameter = assign()
    michaelis_constant: Parameter = assign()
    reaction = RateLaw(
        reactants=[S],
        products=[P],
        rate_law=maximum_velocity * S / (michaelis_constant + S),
    )
