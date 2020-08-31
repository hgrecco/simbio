from simbio import Compartment, Parameter, Simulator, Species
from simbio.reactions import Destruction, Synthesis


class Cell(Compartment):
    C = Species(100)
    O2 = Species(100)
    CO2 = Species(0)

    k = Parameter(1)

    def add_reactions(self):
        yield Synthesis(self.C, self.O2, self.CO2, self.k)
        yield Destruction(self.CO2, self.k)


# Extend from model Cell, not Compartment
class ExtendedCell(Cell):
    # Add new species and parameters
    CO = Species(0)
    k_CO2 = Parameter(1)

    # Override existing species and parameters values
    # explicitly with override=True
    C = Species(130, override=True)
    k = Parameter(0.5, override=True)

    # Add new reactions
    def add_reactions(self):
        yield Synthesis(self.C, self.O2, self.CO, self.k)

    # Override existing reactions explicitly
    def override_reactions(self):
        yield Synthesis(self.C, self.O2, self.CO2, self.k_CO2)  # changes rate parameter


sim = Simulator(ExtendedCell)
t, y = sim.run(10)
