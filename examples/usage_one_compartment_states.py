import matplotlib.pyplot as plt
from simbio import Compartment, Simulator
from simbio.reactions.enzymatic import MichaelisMentenEqApprox

##############

cell = Compartment(name="cell")
C = cell.add_compartment("C")
C.add_species("u", value=1)
C.add_species("p", value=0)
C.add_species("pp", value=1)

cell.C.add_parameter("K", 0.1)
cell.C.add_parameter("D", 0.1)

step1 = MichaelisMentenEqApprox(
    S=cell.C.u, P=cell.C.p, maximum_velocity=cell.C.K, dissociation_constant=cell.C.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.p, P=cell.C.pp, maximum_velocity=cell.C.K, dissociation_constant=cell.C.D,
)

cell.C.add_reaction(step1)
cell.C.add_reaction(step2)


sim = Simulator(cell)
_, df = sim.run(100)

df.plot()
plt.show()
