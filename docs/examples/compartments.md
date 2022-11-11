---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Multiple compartments

Compartments can be nested within another Compartment,
allowing some modularity in the definition of models.
Inner compartments can be extracted,
and simulated independently of the whole model.

```{code-cell} ipython3
import numpy as np

from simbio.components import EmptyCompartment, Species
from simbio.reactions.single import Conversion, Dissociation, Synthesis
from simbio.simulator import Simulator
```

Here,
we define a model consisting of two inner compartments,
both containing hydrogen, oxygen and water.
Water is synthesized in one compartment, and
transported to the other compartment,
where it is dissociated, and
the oxygen and hydrogen transported back to the first compartment.

```{code-cell} ipython3
class Outer(EmptyCompartment):
    class Inner1(EmptyCompartment):
        H2: Species = 1
        O2: Species = 1
        H2O: Species = 0

        create_water = Synthesis(A=2 * H2, B=O2, AB=2 * H2O, rate=2)

    class Inner2(EmptyCompartment):
        H2: Species = 0
        O2: Species = 0
        H2O: Species = 0.1

        electrolysis = Dissociation(AB=2 * H2O, A=2 * H2, B=O2, rate=0.5)

    # Transport between compartments
    water_transport = Conversion(A=Inner1.H2O, B=Inner2.H2O, rate=1)
    H2_transport = Conversion(A=Inner2.H2, B=Inner1.H2, rate=1)
    O2_transport = Conversion(A=Inner2.O2, B=Inner1.O2, rate=1)
```

We can simulate the whole model:

```{code-cell} ipython3
simulator = Simulator(Outer)

t = np.linspace(0, 10, 100)
df = simulator.run(t)
df.head()
```

and just visualize the time evolution of the `H20` species in each compartment,
with the `DataFrame.filter` method followed by `.plot`:

```{code-cell} ipython3
df.filter(like="H2O").plot()
```

But,
we can also simulate a single compartment:

```{code-cell} ipython3
simulator = Simulator(Outer.Inner1)

t = np.linspace(0, 10, 100)
df = simulator.run(t)
df.plot()
```
