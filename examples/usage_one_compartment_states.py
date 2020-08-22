import matplotlib.pyplot as plt
from simbio import Universe
from simbio.reactions.enzymatic import MichaelisMentenEqApprox
from simbio.simulator import PandasSimulator as Simulator

##############

cell = Universe("cell")
C = cell.add_compartment("C")
C.add_species("u", concentration=1)
C.add_species("p", concentration=0)
C.add_species("pp", concentration=1)

cell.add_parameter("K", 0.1)
cell.add_parameter("D", 0.1)
step1 = MichaelisMentenEqApprox(
    S=cell.C.u, P=cell.C.p, maximum_velocity=cell.K, dissociation_constant=cell.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.p, P=cell.C.pp, maximum_velocity=cell.K, dissociation_constant=cell.D,
)

cell.add_reaction(step1)
cell.add_reaction(step2)


sim = Simulator(cell)
_, df = sim.run(100)

df.plot()
plt.show()
