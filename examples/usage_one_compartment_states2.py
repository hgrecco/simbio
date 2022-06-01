import matplotlib.pyplot as plt

from simbio.components import EmptyCompartment
from simbio.reactions.enzymatic import MichaelisMentenEqApprox
from simbio.simulator import Simulator

cell = EmptyCompartment.to_builder(name="cell")
C = cell.add_compartment("C")
C.add_species("u_u", 1)
C.add_species("u_p", 0)
C.add_species("p_u", 0)
C.add_species("p_p", 0)
C.add_parameter("K", 0.1)
C.add_parameter("D", 0.1)

step1 = MichaelisMentenEqApprox(
    S=cell.C.u_u,
    P=cell.C.p_u,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.u_u,
    P=cell.C.u_p,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)
step3 = MichaelisMentenEqApprox(
    S=cell.C.p_u,
    P=cell.C.p_p,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)
step4 = MichaelisMentenEqApprox(
    S=cell.C.u_p,
    P=cell.C.p_p,
    maximum_velocity=cell.C.K,
    dissociation_constant=cell.C.D,
)

C.add_reaction("uu_to_pu", step1)
C.add_reaction("uu_to_up", step2)
C.add_reaction("pu_to_pp", step3)
C.add_reaction("up_to_pp", step4)


sim = Simulator(cell)
_, df = sim.run(range(100))

df.plot()
plt.show()
