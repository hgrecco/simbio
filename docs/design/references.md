# References

A `Compartment` groups `Species` and links them with `Reaction`s. It has to know if a `Species` that appears in one `Reaction` is the same `Species` that appears in another `Reaction`. There are multiple design choices for this. Let's consider them from the point of view of a `CopmartmentBuilder`.

The API for a `CompartmentBuilder` is the following:

```python
class CompartmentBuilder:
    volume: float

    parameters: Mapping[str, set[Parameter]]
    species: Mapping[str, set[Species]]
    reactions: Mapping[str, set[Reaction]]
    groups: Mapping[str, Group]
    compartments: Mapping[str, Compartment]

    def add_parameter(self, name: str, value: float | Parameter):
        ...

    def add_species(self, name: str, value: float | Parameter):
        ...

    def add_reaction(self, name: str, reaction: Reaction):
        ...

    def add_group(self, name: str, group: Group = None):
        ...

    def add_compartment(self, name: str, compartment: Compartment = None):
        ...

    def rename(self, old_name: str, new_name: str):
        ...

    def remove(self, name: str, value=None):
        ...
```

## Species

A `Species` cannot be created *outside* a `Compartment`. If not, the same `Species` could be added to a subcompartment:

```python
cell = CompartmentBuilder()
nucleus = cell.add_compartment("nucleus")

A = Species(0)
cell.add_species("A", A)  # error
nucleus.add_species("A", A)  # error
```

or, by reference to a `Species` existing inside a `Compartment`:

```python
cell = CompartmentBuilder()
nucleus = cell.add_compartment("nucleus")

cell.add_species("A", 0)
nucleus.add_species("A", cell.A)  # error
```

Hence, the API only allow to create `Species` from a `float`, or a `Parameter`:

```python
cell = CompartmentBuilder()

# from float
A = cell.add_species("A", 0)

# from Parameter
k = cell.add_parameter("k", 0)
B = cell.add_species("B", k)
```

But it must deny to create a `Species` from a "free" `Parameter`:

```python
cell = CompartmentBuilder()

k_free = Parameter(0)
A = cell.add_species("A", k_free)  # error

k = cell.add_parameter("k", 0)
A = cell.add_species("A", k)  # ok
```

To distinguish between those cases, there are two options:

### Option 1

We search for the `k_free` inside `cell`. To search, we can either:

1. check for identity (`is`) within `cell.parameters`

1. If `Parameter` knows its name, we check for \`k_free is cell.parameters\[k_free.name\]

This approach excludes using upper level parameters:

```python
cell = CompartmentBuilder()
k = cell.add_parameter("k", 1)

nucleus = cell.add_compartment("nucleus")
A = nucleus.add_species("A", k)
```

as `k not in nucleus.parameters.values()`.

### Option 2

`k_free` and `k`, the variable `k` cannot be a `Parameter` instance.

## Reactions

To add a `Reaction` to a given `Compartment`, its `Species` must be reachable from the `Compartment`, that is, belonging to it or any of its subcompartments.

```python
cell = CompartmentBuilder()
nucleus = cell.add_compartment("nucleus")

A = cell.add_species("A", 0)
k = cell.add_parameter("k", 1)

# This is fine
cell.add_reaction("create_A", Creation(A, k))

# This is raises an Exception
nucleus.add_reaction("create_A", Creation(A, k))
```

`A` and `k` cannot be only names (`str`), as this would not raise an exception:

```python
# continuing from above
nucleus.add_species("A", 0)
nucleus.add_parameter("k", 1)

# This must still raise an Exception, as A is cell.A and k is cell.k
nucleus.add_reaction("create_A", Creation(A, k))
```

### Option 1

To check if a reaction's `Species` is inside the `Compartment`, it is checked by identity: `id()`. We would have to check every subcompartment to see if this `Species`is *reachable*.

### Option 2

Have a reference to its owning `Compartment`.

But consider this case, with two levels of `Compartment`:

```python
tissue = CompartmentBuilder()
cell = tissue.add_compartment("cell")
nucleus = cell.add_compartment("nucleus")

A = tissue.add_species("A", 0)
B = nucleus.add_species("B", 0)
tissue.add_reaction("transport", Convert(A, B, rate=1))  # allower?
```

If adding that reaction is allowed, there are two ways to check that `B` is reachable from `tissue`:

- Either `A`not only needs to know that its parent `Compartment` is `nucleus`, but `nucleus` would have to know its parent `Comparment`
