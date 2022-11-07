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

# Compilers

By default,
the `Simulator` uses the `NumpyCompiler`,
which compiles the model to solve as an ODE system.

But the compiler can be changed,
for instance,
for other types of integration,
such a stochastic simulations,

For large models,
we have implemented a `NumbaCompiler`,
which compiles the RHS (right hand side) using `numba`,
providing a significant speed boost.

## NumbaCompiler

When integrating a large model,
such as `Corbat2018`,
which has 82 mass-action reactions between 69 species,
it is significantly faster to use the `NumbaCompiler`.

Using the default `NumpyCompiler`:

```{code-cell} ipython3
import numpy as np
from simbio.models.corbat2018 import Corbat2018_extrinsic
from simbio.simulator import Simulator

t = np.linspace(0, 30_000, 100)
sim = Simulator(Corbat2018_extrinsic)
%time df = sim.run(t)
```

To switch to the `NumbaCompiler`,
we must import it from `simbio.compilers`,
and pass it to `Simulator`:

```{code-cell} ipython3
from simbio.compilers.numba import NumbaCompiler

sim = Simulator(Corbat2018_extrinsic, compiler=NumbaCompiler)
%time df = sim.run(t)
```

The first run is slower,
as it includes the `numba` compilation time.
But subsequent runs are lightning fast,
as the compilation is cached:

```{code-cell} ipython3
%time df = sim.run(t)
```
