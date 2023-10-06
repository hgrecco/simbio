# Introducing poincaré and SimBio

Poincaré is a new Python-based library to define and simulate dynamical systems.
Trying not to reinvent (much of) the wheel,
it uses modern Python syntax to define and compose models in a compact way.
This allows us to take advantage of the huge investment on tooling from the broader Python community
such as static type checkers, code linters and formatters, autocomplete and refactoring features from IDEs, among others.

Using standard libraries from the PyData ecosystem,
by default, poincaré compiles into a first-order ODE system using NumPy arrays, and uses solvers from SciPy.
But it also provides different backends such as Numba,
which compiles just-in-time to LLVM code,
providing a significant speed boost,
or JAX, which provides autodifferentiation tools targeted for ML.
Additionally, it supports units using the Pint library.

SimBio is built on top of poincaré,
adding some components for reaction-based models used in systems biology.
It provides some predefined building blocks for the most common reactions,
but allows easily to create your own.
Finally, it implements an importer and exporter to SBML,
allowing to interexchange models with the COMBINE community.
We hope that it is simple enough for beginners,
but powerful for power-users with the possibility to extend and compose with the large Python ecosystem.
