import numpy as np
from pytest import mark
from simbio.core import Compartment, Simulator
from simbio.reactions import compound, enzymatic, single

reactions = []
for mod in (single, compound, enzymatic):
    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type(Compartment)):
            reactions.append(value)


@mark.parametrize("reaction", reactions)
def test_reactions(reaction):
    model = reaction(**dict.fromkeys(reaction._required, 0))
    times = np.linspace(0, 1, 10)
    Simulator(model).solve(times=times)
