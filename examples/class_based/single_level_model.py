from simbio import Compartment, Parameter, Simulator, Species
from simbio.reactions import Synthesis


# Creating a Comparment
class Cell(Compartment):
    # Adding Species and ther initial concentration
    C = Species(100)
    O2 = Species(100)
    CO = Species(0)
    CO2 = Species(0)

    # Adding Parameters and their values
    k_CO = Parameter(1)
    k_CO2 = Parameter(2)

    # Adding reactions between Species
    def add_reactions(self):
        yield Synthesis(2 * self.C, self.O2, self.CO, self.k_CO)
        yield Synthesis(self.C, self.O2, self.CO2, self.k_CO2)


# Passing the Compartment to the Simulator
sim = Simulator(Cell)
t, y = sim.run(10)
