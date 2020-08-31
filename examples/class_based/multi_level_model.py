from simbio import Compartment, Parameter, Simulator, Species
from simbio.reactions import Conversion, Synthesis


class Cell(Compartment):
    # Parameters at Cell-level
    k = Parameter(1)

    # Reactions at Cell-level
    def add_reactions(self):
        # Transports CO2 from Cytoplasm to Nucleus
        yield Conversion(self.Cytoplasm.CO2, self.Nucleus.CO2, self.k)

    # Inner Compartment
    class Cytoplasm(Compartment):
        C = Species(100)
        O2 = Species(100)
        CO2 = Species(0)
        k = Parameter(2)

        # Reaction at Cytoplasm-level
        def add_reactions(self):
            # Converts C and O2 to CO2
            yield Synthesis(self.C, self.O2, self.CO2, self.k)

    # Inner Compartment
    class Nucleus(Compartment):
        CO2 = Species(0)


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
