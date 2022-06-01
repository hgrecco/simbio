from simbio.components import EmptyCompartment, Parameter, Species
from simbio.reactions.single import Conversion, Synthesis
from simbio.simulator import Simulator


class Cell(EmptyCompartment):
    # Parameters at Cell-level
    k: Parameter = 1

    # Inner Compartment
    class Cytoplasm(EmptyCompartment):
        C: Species = 100
        O2: Species = 100
        CO2: Species = 0
        k: Parameter = 2

        # Reaction at Cytoplasm-level
        # Converts C and O2 to CO2
        synthesize_CO2 = Synthesis(C, O2, CO2, k)

    # Inner Compartment
    class Nucleus(EmptyCompartment):
        CO2: Species = 0

    # Reactions at Cell-level
    # Transports CO2 from Cytoplasm to Nucleus
    transport_CO2 = Conversion(Cytoplasm.CO2, Nucleus.CO2, k)


# Full simulation
sim = Simulator(Cell)
t, y = sim.run(10)

# Cytoplasm-only simulation
sim = Simulator(Cell.Cytoplasm)
t, y = sim.run(10)

# Nucleus-only simulation
# No reactions at Nucleus-level, should return an empty tuple.
sim = Simulator(Cell.Nucleus)
t, y = sim.run(10)
