![Package](https://img.shields.io/pypi/v/simbio?label=simbio)
![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/pypi/l/simbio?label=license)
![PyVersion](https://img.shields.io/pypi/pyversions/simbio?label=python)
[![CI](https://github.com/hgrecco/simbio/actions/workflows/ci.yml/badge.svg)](https://github.com/hgrecco/simbio/actions/workflows/ci.yml)

# SimBio

`simbio` is a Python-based package for simulation of Chemical Reaction Networks (CRNs).
It extends [`poincare`](https://github.com/maurosilber/poincare),
a package for modelling dynamical systems,
to add functionality for CRNs.

## Usage

To create a system with two species $A$ and $B$
and a reaction converting $2A \\rightarrow B$ with rate 1:

```python
>>> from simbio import Compartment, Species, RateLaw, initial
>>> class Model(Compartment):
...    A: Species = initial(default=1)
...    B: Species = initial(default=0)
...    r = RateLaw(
...        reactants=[2 * A],
...        products=[B],
...        rate_law=1,
...    )
```

This corresponds to the following system of equations

$$
\\begin{cases}
\\frac{dA}{dt} = -2 \\
\\frac{dB}{dt} = +1
\\end{cases}
$$

with initial conditions

$$
\\begin{cases}
A(0) = 1 \\
B(0) = 0
\\end{cases}
$$

In CRNs,
we usually deal with [mass-action](https://en.wikipedia.org/wiki/Law_of_mass_action) reactions.
Using `MassAction` instead of `Reaction` automatically adds the reactants to the rate law:

```python
>>> from simbio import MassAction
>>> class MassActionModel(Compartment):
...    A: Species = initial(default=1)
...    B: Species = initial(default=0)
...    r = MassAction(
...        reactants=[2 * A],
...        products=[B],
...        rate=1,
...    )
```

generating the following equations:

$$
\\begin{cases}
\\frac{dA}{dt} = -2 A^2 \\
\\frac{dB}{dt} = +1 A^2
\\end{cases}
$$

To simulate the system,
use the `Simulator.solve` which outputs a `pandas.DataFrame`:

```python
>>> from simbio import Simulator
>>> Simulator(MassActionModel).solve(save_at=range(5))
             A         B
time
0     1.000000  0.000000
1     0.333266  0.333367
2     0.199937  0.400032
3     0.142798  0.428601
4     0.111061  0.444470
```

For more details into SimBio's capabilities,
we recommend reading [poincaré's README](https://github.com/maurosilber/poincare).

## SBML

SimBio can import models from Systems Biology Markup Language (SBML) files:

```python
>>> from simbio.io import sbml
>>> sbml.load("repressilator.sbml")
Elowitz2000 - Repressilator
-----------------------------------------------------------------------------------
type          total  names
----------  -------  --------------------------------------------------------------
variables         6  PX, PY, PZ, X, Y, Z
parameters       17  cell, beta, alpha0, alpha, eff, n, KM, tau_mRNA, tau_prot, ...
equations        12  Reaction1, Reaction2, Reaction3, Reaction4, Reaction5, ...
```

or download them from the [BioModels](https://www.ebi.ac.uk/biomodels/) repository:

```python
>>> from simbio.io import biomodels
>>> biomodels.load_model("BIOMD12")
Elowitz2000 - Repressilator
-----------------------------------------------------------------------------------
type          total  names
----------  -------  --------------------------------------------------------------
variables         6  PX, PY, PZ, X, Y, Z
parameters       17  cell, beta, alpha0, alpha, eff, n, KM, tau_mRNA, tau_prot, ...
equations        12  Reaction1, Reaction2, Reaction3, Reaction4, Reaction5, ...
```

## Installation

It can be installed from [PyPI](https://pypi.org/p/simbio) with `pip`:

```
pip install simbio
```

Or, to additionally install the SBML importer:

```
pip install simbio[io]
```
