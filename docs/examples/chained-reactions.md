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

# Chained reactions

+++

To showcase the [dynamic or programmatic model creation](../model/dynamic.md),
we will build a model consisting of a circular chain of $N$ reactions,

$$
\begin{cases}
X_1 \rightarrow X_{2} \\
\ldots \\
X_i \rightarrow X_{i+1} \\
\ldots \\
X_N \rightarrow X_{1}
\end{cases}
$$

and simulate it for different values of $N$.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from simbio.components import EmptyCompartment
from simbio.reactions import single
from simbio.simulator import Simulator
```

To define a model programmatically,
we need a `Builder` instance,
which can be created from a `Compartment.to_builder()` method.
`Builder` has several `add_*` methods to create species or add reactions.

```{code-cell} ipython3
def cyclic_reaction(N_steps):
    builder = EmptyCompartment.to_builder()

    # First species
    x_pre = builder.add_species("x0", 1)

    # Chained reactions
    for i in range(1, N_steps):
        x_post = builder.add_species(f"x{i}", 0)
        builder.add_reaction(f"r{i}", single.Conversion(A=x_pre, B=x_post, rate=1))
        x_pre = x_post

    # Reaction from last to first species
    x_post = builder.x0
    builder.add_reaction(f"r0", single.Conversion(A=x_pre, B=x_post, rate=1))

    return builder.build()
```

With the `cyclic_reaction` function,
we can build a model of $N$ reactions,
and simulate it for different values of $N$:

```{code-cell} ipython3
t = np.linspace(0, 30, 100)
N_steps = (2, 5, 10)

fig, axes = plt.subplots(1, len(N_steps), sharey=True, figsize=(12, 3))
for ax, N in zip(axes, N_steps):
    model = cyclic_reaction(N)
    Simulator(model).run(t).plot(ax=ax, legend=False).set(title=f"N = {N}")
```
