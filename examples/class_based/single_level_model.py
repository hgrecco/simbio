from simbio.components import EmptyCompartment, Parameter, Species
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator


# Creating a Comparment
class Cell(EmptyCompartment):
    # Adding Species and ther initial concentration
    C: Species = 100
    O2: Species = 100
    CO: Species = 0
    CO2: Species = 0

    # Adding Parameters and their values
    k_CO: Parameter = 1
    k_CO2: Parameter = 2

    # Adding reactions between Species
    synthesize_CO = Synthesis(A=2 * C, B=O2, AB=CO, rate=k_CO)
    synthesize_CO2 = Synthesis(A=C, B=O2, AB=CO2, rate=k_CO2)


# Passing the Compartment to the Simulator
sim = Simulator(Cell)
df = sim.run(range(10))
