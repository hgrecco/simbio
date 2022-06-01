from simbio.components import EmptyCompartment, Parameter, Species
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator


class Cell(EmptyCompartment):
    C: Species = 10
    O2: Species = 10
    CO2: Species = 0
    k: Parameter = 1

    synthesize = Synthesis(A=C, B=O2, AB=CO2, rate=k)


# Overrides concentrations and parameters for this Simulator
sim = Simulator(Cell, values={Cell.CO2: 5, Cell.k: 2, "O2": 15})

# Overrides concentrations and parameters for this run
t, y = sim.run(range(10), values={Cell.C: 20})
