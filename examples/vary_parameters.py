from simbio import Compartment, Parameter, Simulator, Species
from simbio.reactions import Synthesis


class Cell(Compartment):
    C = Species(10)
    O2 = Species(10)
    CO2 = Species(0)
    k = Parameter(1)

    def add_reactions(self):
        yield Synthesis(self.C, self.O2, self.CO2, self.k)


# Overrides concentrations and parameters for this Simulator
sim = Simulator(Cell, values={Cell.CO2: 5, Cell.k: 2, "O2": 15})

# Overrides concentrations and parameters for this run
t, y = sim.run(range(10), values={Cell.C: 20})
