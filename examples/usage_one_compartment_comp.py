import matplotlib.pyplot as plt
from scipy.integrate import RK45
from simbio import Compartment
from simbio.reactions import ReversibleSynthesis

##############

cell = Compartment("cell")
cell.add_reactant("C", concentration=2)
cell.add_reactant("O2", concentration=1)
cell.add_reactant("CO2", concentration=0)
cell.add_parameter("forward_rate", 0.1)
cell.add_parameter("reverse_rate", 0.05)

step1 = ReversibleSynthesis(
    A=cell.C,
    B=cell.O2,
    AB=cell.CO2,
    forward_rate=cell.forward_rate,
    reverse_rate=cell.reverse_rate,
)
cell.add_reaction(step1)

initial = cell.build_concentration_vector()
rhs = cell.build_ip_rhs()
names = cell.names()

# Just a stupid test
assert rhs(0, initial).shape == initial.shape

solver = RK45(rhs, 0, initial, 100)

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
