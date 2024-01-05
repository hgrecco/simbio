import numpy as np
from pytest import mark

from ..core import Compartment, Parameter, RateLaw, Simulator, Species, assign, initial
from ..reactions import compound, enzymatic, single

reactions = []
for mod in (single, compound, enzymatic):
    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type(Compartment)):
            reactions.append(value)


@mark.parametrize("reaction", reactions)
def test_reactions(reaction):
    model = reaction(**dict.fromkeys(reaction._required, 1))
    sim = Simulator(model)
    sim.solve(save_at=np.linspace(0, 1, 10))


def test_reaction_with_species():
    class Model(Compartment):
        s: Species = initial(default=0)
        k: Parameter = assign(default=0)
        r_with_species = RateLaw(reactants=[s], products=[], rate_law=k * s)
        r_with_variable = RateLaw(reactants=[s], products=[], rate_law=k * s.variable)

    assert Model.r_with_species.rate_law == Model.r_with_variable.rate_law
