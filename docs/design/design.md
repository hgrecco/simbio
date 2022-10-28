# Implementation details

## Species

The `Species` class is quite simple:

```python
class Species:
    value: float | Parameter
```

Its initial concentration can be a number (`float`) or can be resolved later when using a `Parameter`. Using a `Parameter` allows to easily link multple initial concentrations.

## Parameter

The `Parameter` class is similar to `Species`:

```python
class Parameter:
    value: float | Parameter
```

As `Parameter`s can depend on other `Parameter`s, they form a DAG, which is resolved before simulation.

This allows the following. Imagine we have two `Parameter`s, `kA` and `kB`, such that both depend on a third `Parameter`, `k`:

```python
class Model(Compartment):
    k = Parameter(1)
    kA = Parameter(k)
    kB = Parameter(k)
```

During simulation, we can vary `k`, which in turns varies both `kA` and `kB` in the same way. But we can also set them independently. This useful if a set A of Species/Reactions depends on `kA` and other set B dependes on `kB`.

## Compartments

A `Compartment` provides the following read-only attributes:

```python
class Compartment:
    volume: float

    parameters: Mapping[str, Parameter]
    species: Mapping[str, Species]
    reactions: Mapping[str, Reaction]
    groups: Mapping[str, Groups]
    compartments: Mapping[str, Compartments]
```

### Nested Comaprtments

Compartments can be nested inside a compartment, generating a tree-like structure. Any of these sub-Compartments could be selected and simulated independently. Hence, all Reactions in a given Compartment must relate Species "reachable" from said Compartment. That is, Species defined within that Compartment or any of its sub-Compartments.

Note: it does not imply that Reactions between two sub-Compoartments cannot exist, but that the Reaction must be defined in its common parent.

For instance, the Reaction corresponding to a transport from a Species in the Nucleus of a Cell to its Cytoplasm lives in the Cell itself, not in its sub-Compartments:

```
Cell
|---Nucleus
|   |---A: Species
|
|---Cytoplasm
|   |---A: Species
|
|---Reaction: Nucleus.A -> Cytoplasm.A
```

## Reactions

The `Reaction` class corresponds to a simple reaction, where reactants are converted to products at a given rate:

```python
class Reaction:
    species: Mapping[str, Stoichiometry]
    rates: Mapping[str, float | Parameter]
    rate_law: callable[]

    reactants: ?
    products: ?
    equivalence: ?
```

```python
class SingleReaction:
    reactants: Set[Stoichiometry]
    products: Set[Stoichiometry]
    rate: float | Parameter
```

where `Stoichiometry` corresponds to

```python
class Stoichiometry:
    species: Species
    number: float
```

It implies the following differential equations:

1. $A \\rightarrow B$

   - $\\dot{A} = -kA$
   - $\\dot{B} = +kA$

1. A + B -> B

   - $\\dot{A} = -kAB$
   - $\\dot{B} = 0$

1. 2A -> B

   - $\\dot{A} = -2 k A^2 / 2!$
   - $\\dot{B} = -k A^2 / 2!$

### Uniqueness of Reactions

To avoid inadvertently adding the same reaction more than once, two restrictions are enforced:

1. a Reaction must be unique within a given Compartment.
1. a Reaction can only be added to the first common parent of its Species.

For this purpose, two reactions are equivalent if they have the same set of reactants and products, independently of its rate.

Extending the previous example:

```
Tissue
|---Cell
|   |---Nucleus
|   |   |---A: Species
|   |
|   |---Cytoplasm
|   |   |---A: Species
|   |
|   |---Reaction: Nucleus.A -> Cytoplasm.A  # ok
|---Reaction: Nucleus.A -> Cytoplasm.A  # not ok
```

## Group

`Group` is similar to `Compartment`, but it is only a logical "compartment":

```python
class Group:
    parameters: Mapping[str, Parameter]
    species: Mapping[str, Species]
    reactions: Mapping[str, Reaction]
    groups: Mapping[str, Groups]
```

In contrast to `Compartment`, `Group`s can be used to define "macros", by leaving *uninitialized* `Species` or `Parameter`s as annotations:

```python
@dataclass  # optional for type-hints
class MyGroup(Group):
    """A -> B"""

    A: Species  # uninitialized
    k: Parameter  # uninitialized
    B = Species(0)
    convert = Convert(A, B, rate=k)
```

And then used as:

```python
class Model(Compartment):
    X = Species(1)
    group_1 = MyGroup(A=X, rate=1)
    group_2 = MyGroup(A=X, rate=2)
```

Model has 3 distinct `Species`:

- `X` (which is also `group_1.A` and `group_2.A`)
- `group_1.B`
- `group_2.B`

and two `Reaction`s:

- `X -> group_1.B` with `rate=1`
- `X -> group_2.B` with `rate=2`

Note that the reactions `group_1.convert` and `group_2.convert` does not "belong" to their respective groups, but to `Model`, which is the first common parent between the `Species` in the `Reaction`s.
