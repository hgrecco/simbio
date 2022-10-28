# SimBio

## Biological units

SimBio has 3 main classes representing biological entities or processes.

- Species: it represents a class of biological entities. It has an initial concetration or number of units.
- Reaction: it dictates a tranformation between Species at a given rate.
- Compartment: a volume in which a set of Species live and Reactions between them take place.

Additionally, there are other two main classes which simplify modelling:

- Parameter: a numeric value which allows to link some Species initial concentrations, or link some Reaction rates.
- Group: a logical grouping of group Species, Parameters and Reactions. Allows to create user-defined "macros". For instance, compound reactions are implemented as Groups.

## Nested models

A Model is composed of a Compartment, its Species and Reactions. But Compartments may be defined inside Compartments, generating a tree-like structure. Any sub-Compartment can be selected independently and simulated.

## Model comparisons and equivalence classes

Model can be compared and composed with set-like operators:

- union: `|` (`__or__`)
- intersection: `&` (`__and__`)
- difference: `-` (`__sub__`)
- symmetric difference: `^` (`__xor__`)

Additionally, different equivalence classes are defined to compare models. From less to more restrictive, where each implies the previous equivalence, they are:

1. Topological equivalence

   The same species are connected by (possibly different) reactions.

1. Reaction equivalence

   The reactions have the same rate law, but possibly having a different rate constant.

1. Parametric equivalence

   The reactions have the same rate constants.

1. Equality

   The same initial conditions for the Species.

The set operators use the last equivalence class, Equality, to compare models.

## Modular API

The API is divided on 3 independent modules:

### 1. Building

Declaration of Species and Reactions in a Model. It provides two APIs to create a Model:

- a class-based API, implemented as a DSL using metaclasses. To support IDE features such as (static) typing hints and refactoring, it doesn't deviate much from standard Python classes.
- a builder pattern that allows to dynamically define a model, but provides less help from IDEs. It is useful to test many variations of a Model in a for-loop.

### 2. Compilation

From an input Model, it generates a simulator function. At this time, there are two `Compilator`s implemented:

- a numpy-based ODE function
- a numba-jitted ODE function

But custom compilators might be implemented, for different types of simulation, such as one that produces an SDE function, or one that performs certain optimizations or approximations.

### 3. Simulation

Provides a Simulator adapter class that defines an API to simplify simulation. It mediates between a Model, a Compiler and a Solver.

Downstream packages just need to know this API to add additional functionality, such as performing a parameter search.

## Other features

- Unit support: it uses [Pint](https://github.com/hgrecco/pint).
