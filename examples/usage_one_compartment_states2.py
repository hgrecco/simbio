import matplotlib.pyplot as plt
from scipy.integrate import RK45
from simbio import Compartment, Reactant
from simbio.reactions.enzymatic import MichaelisMentenReduced

##############

cell = Compartment("cell")
C = Reactant("C", concentration=1, states=dict(a="u p", b="u p"))
cell.add_reactant(C)
step1 = MichaelisMentenReduced(
    S=cell.C.u_u,
    P=cell.C.p_u,
    enzyme_concentration=0.1,
    michaelis_constant=0.1,
    catalytic_rate=0.1,
)
step2 = MichaelisMentenReduced(
    S=cell.C.u_u,
    P=cell.C.u_p,
    enzyme_concentration=0.2,
    michaelis_constant=0.1,
    catalytic_rate=0.1,
)
step3 = MichaelisMentenReduced(
    S=cell.C.p_u,
    P=cell.C.p_p,
    enzyme_concentration=0.1,
    michaelis_constant=0.1,
    catalytic_rate=0.1,
)
step4 = MichaelisMentenReduced(
    S=cell.C.u_p,
    P=cell.C.p_p,
    enzyme_concentration=0.1,
    michaelis_constant=0.1,
    catalytic_rate=0.1,
)

cell.add_reaction(step1)
cell.add_reaction(step2)
cell.add_reaction(step3)
cell.add_reaction(step4)

initial = cell.build_concentration_vector()
rhs = cell.build_ip_rhs()
names = cell.names()
# Just a stupid test
assert rhs(0, initial).shape == initial.shape

solver = RK45(rhs, 0, initial, 150)

print("Starting ...")
t_values = []
y_values = []
for _ in range(100):
    # get solution step state
    solver.step()
    t_values.append(solver.t)
    y_values.append(solver.y)
    # break loop after modeling is finished
    if solver.status == "finished":
        break


plt.plot(t_values, y_values)
plt.legend(names)
plt.show()