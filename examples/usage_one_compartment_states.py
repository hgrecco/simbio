import matplotlib.pyplot as plt

from simbio.components import EmptyCompartment
from simbio.reactions.enzymatic import MichaelisMentenEqApprox
from simbio.simulator import Simulator

##############

cell = EmptyCompartment.to_builder(name="cell")
C = cell.add_compartment("C")
C.add_species("u", value=1)
C.add_species("p", value=0)
C.add_species("pp", value=1)

cell.C.add_parameter("K", 0.1)
cell.C.add_parameter("D", 0.1)

step1 = MichaelisMentenEqApprox(
    S=cell.C.u,
    P=cell.C.p,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.p,
    P=cell.C.pp,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)

cell.C.add_reaction("u_to_p", step1)
cell.C.add_reaction("p_to_pp", step2)

cell = cell.build()

sim = Simulator(cell)
_, df = sim.run(range(100))

df.plot()
plt.show()
