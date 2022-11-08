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

# Dynamic or programmatic

+++

To create a model dynamically,
we need to create a `Builder` instance from a `Compartment`:

```{code-cell} ipython3
from simbio.components import EmptyCompartment
from simbio.reactions import single


builder = EmptyCompartment.to_builder()
```

A `Builder` add several `add_*` methods,
to add species, parameters and reactions.

For instance,
to add a species:

```{code-cell} ipython3
A = builder.add_species(name="A", value=1)

A
```

The variable `A` is a `Reference` to the `Species`,
which we can use in reactions:

```{code-cell} ipython3
builder.add_reaction("create_A", single.Creation(A=A, rate=1))
```

We can also obtain a `Reference` to `A` using attribute access:

```{code-cell} ipython3
builder.A
```

When we finished building the model,
we need to use the `.build()` method
to obtain the underlying `Compartment`:

```{code-cell} ipython3
model = builder.build()
```

Then,
it can be used in a `Simulator`,
just as a class-based model:

```{code-cell} ipython3
import numpy as np
from simbio.simulator import Simulator

t = np.linspace(0, 10, 100)
Simulator(model).run(t).plot()
```

## Inheriting and combining models

We can inherit from a previous model
by calling it `.to_builder()` method:

```{code-cell} ipython3
from simbio.components import Species


class Base(EmptyCompartment):
    A: Species = 1


builder = Base.to_builder()
```

Or we can use the update method on an existing `Builder` instance:

```{code-cell} ipython3
builder = EmptyCompartment.to_builder()
builder.update(Base)
```

As in the class-based models,
adding an existing species raises an error:

```{code-cell} ipython3
---
tags: [raises-exception]
---
builder.add_species("A", 2)
```

If we want to replace it,
we must explicitly tell `SimBio`:

```{code-cell} ipython3
builder.add_species("A", 2, replace=True)
```

# Example: chained reactions

We will build a model consisting of a circular chain of $N$ reactions:

$$ X_i \rightarrow X_{i+1} $$

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

And then run the model for different values of $N$:

```{code-cell} ipython3
import matplotlib.pyplot as plt

t = np.linspace(0, 30, 100)
N_steps = (2, 5, 10)

fig, axes = plt.subplots(1, len(N_steps), sharey=True, figsize=(12, 3))
for ax, N in zip(axes, N_steps):
    model = cyclic_reaction(N)
    Simulator(model).run(t).plot(ax=ax, legend=False).set(title=f"N = {N}")
```
