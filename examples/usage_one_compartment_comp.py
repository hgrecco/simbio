import matplotlib.pyplot as plt

from simbio.components import EmptyCompartment
from simbio.reactions.compound import ReversibleSynthesis
from simbio.simulator import Simulator

cell = EmptyCompartment.to_builder(name="cell")
cell.add_species("C", 2)
cell.add_species("O2", 1)
cell.add_species("CO2", 0)
cell.add_parameter("forward_rate", 0.1)
cell.add_parameter("reverse_rate", 0.05)

step1 = ReversibleSynthesis(
    A=cell.C,
    B=cell.O2,
    AB=cell.CO2,
    forward_rate=cell.forward_rate,
    reverse_rate=cell.reverse_rate,
)
cell.add_reaction("rev_synth", step1)

sim = Simulator(cell)
_, df = sim.run(range(100))

df.plot()
plt.show()
