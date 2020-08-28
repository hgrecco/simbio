from simbio import Simulator, Universe
from simbio.reactions import Conversion

cell = Universe("cell")
cell.add_species("A", 10)
cell.add_species("B")
cell.add_parameter("k", 1)
cell.add_reaction(Conversion(cell.A, cell.B, cell.k))

# Observables
sim = Simulator(cell, observables=(cell.A,))
t, y = sim.run(range(10))

assert y.shape == (10, 1)
