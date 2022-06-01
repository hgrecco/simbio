from simbio.components import EmptyCompartment, Override, Parameter, Reaction, Species
from simbio.reactions.single import Destruction, Synthesis
from simbio.simulator import Simulator


class Cell(EmptyCompartment):
    C: Species = 100
    O2: Species = 100
    CO2: Species = 0

    k: Parameter = 1

    synthesize_CO2 = Synthesis(A=C, B=O2, AB=CO2, rate=k)
    remove_CO2 = Destruction(A=CO2, rate=k)


# Extend from model Cell, not Compartment
class ExtendedCell(Cell):
    # Reuse previous Species
    O2: Species
    CO2: Species

    # Add new species and parameters
    CO: Species = 0
    k_CO2: Parameter = 1

    # Override existing species and parameters values
    C: Species[Override] = 130
    k: Parameter[Override] = 0.5

    # Add new reactions
    synthesize_CO = Synthesis(A=C, B=O2, AB=CO, rate=k)  # noqa: F821

    # Override existing reactions explicitly
    synthesize_CO2: Reaction[Override] = Synthesis(
        A=C, B=O2, AB=CO2, rate=k_CO2  # noqa: F821
    )  # changes rate parameter


sim = Simulator(ExtendedCell)
t, y = sim.run(10)
