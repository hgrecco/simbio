# Implementation details

## Species

The `Species` class is quite simple:

```python
class Species:
    value: float | Parameter
```

Its initial concentration can be a number (`float`) or can be resolved later when using a `Parameter`. Using a `Parameter` allows to easily link multple initial concentrations.

## Parameter

The `Parameter` class is similar:

```python
class Species:
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

The `Reaction` class corresponds to a simple reaction.

```python
class Reaction:
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

### Uniqueness of Reactions

To avoid inadvertently adding the same Reaction more than once, there are two restrictions:

1. a Reaction must be unique within a given Compartment.
2. a Reaction can only be added to the first common parent of its Species.

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

## Groups

- Dataclasses
- HungryGroups: cannot be nested (how would they be initialized?).

## DSL

```python
class 
```

- Override MRO: might result in Method Resolution Error.
- Self object or annotation: to provide inherited components.
