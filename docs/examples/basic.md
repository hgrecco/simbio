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

# Basic

We will define a simple model of
water creation from hydrogen and oxygen.

First,
we need to import `EmptyCompartment` and `Species`,
a `Synthesis` reaction,
and a `Simulator` to integrate the equations.

```{code-cell} ipython3
import numpy as np

from simbio.components import EmptyCompartment, Species
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator
```

To define the model,
we create 3 species,
corresponding to
hydrogen $H₂$, oxygen $O₂$, and water $H₂O$,
with initial conditions of `1`, `1` and `0`,
respectively.
And we add a `create_water` reaction,
corresponding to $2 H₂ + O₂ → 2 H₂ O$,
with a rate of `1`.

```{code-cell} ipython3
class Model(EmptyCompartment):
    H2: Species = 1
    O2: Species = 1
    H2O: Species = 0

    create_water = Synthesis(A=2 * H2, B=O2, AB=2 * H2O, rate=1)
```

To simulate it,
we feed the model named `Model` into `Simulator`,
and use the `.run()` method.
It will compile and integrate an `ODE`-based simulation,
returning a `pandas.DataFrame` with the result:

```{code-cell} ipython3
simulator = Simulator(Model)

t = np.linspace(0, 10, 100)
df = simulator.run(t)
df.head()
```

To visualize the time evolution,
we can use the `DataFrame.plot` method:

```{code-cell} ipython3
df.plot()
```
