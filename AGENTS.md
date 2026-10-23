# AGENTS.md — simbio

Instructions for coding agents working **on** this repository. User
documentation is at https://dyscolab.github.io/simbio. Record user-visible
changes in [CHANGELOG.md](CHANGELOG.md).

## Project overview

simbio models chemical reaction networks (CRNs) on top of poincare. It adds
three things to poincare's existing reaction primitives:

- **compartments with volumes**, and species tracked as amounts or
  concentrations,
- a **library of reaction motifs** (creation, conversion, Michaelis–Menten,
  and others),
- **I/O**: SBML import, MathML import and export, BioModels download, and
  networkx graphs.

simbio does **not** have its own simulator or compiler. Simulation is
`poincare.Simulator`, and stochastic simulation is
`poincare.reactions.rebop.RebopSimulator`, re-exported here. `Reactant`,
`RateLaw`, `MassAction`, `AbsoluteRateLaw` and `System` are also defined in
poincare and only re-exported by `simbio/__init__.py`. Typical tasks are
fixing compartment and volume semantics, adding reaction motifs, and
widening SBML/MathML support.

## Repository map

| Path | Responsibility | Touch when |
| --- | --- | --- |
| `src/simbio/__init__.py` | Public namespace. Re-exports poincare symbols and adds simbio ones | Changing the public API |
| `src/simbio/core.py` | `Species` (a `Variable` with a `concentration` flag), `Volume`, `Compartment`, constructors (`amount`, `concentration`, `reaction_amount`, `reaction_concentration`, `volume`), `compensate_volume` / `make_concentration` registrations | Compartment and volume semantics |
| `src/simbio/reactions/` | Reaction motifs as `System` subclasses (`single.py`, `compound.py`, `enzymatic.py`) | Adding or fixing a motif |
| `src/simbio/io/sbml/` | `from_libsbml.Converter` (libsbml → dataclasses in `types.py`) and `importer.SBMLImporter` (dataclasses → dynamic poincare `System`), `load`/`loads` | SBML support |
| `src/simbio/io/mathML/` | MathML ↔ symbolite (`importer.py`, `exporter.py`, `to_symbolite.py`, `symbol.py`) | Math expression import and export |
| `src/simbio/io/{biomodels.py,graph/,substitute_by_name.py}` | BioModels fetch, networkx graphs, name-based substitution | Those features |
| `src/simbio/latex.py` | `model_report` with a reactions section, on top of `poincare.printing.latex` | Reports |
| Tests | `test_core.py`, `reactions/test_reactions.py`, `io/mathML/test_mathML.py`, `io/sbml/test_importer.py`, `io/sbml/tests/test_sbml_test_suite.py` | Always |

## Architecture and core abstractions

- **Volume compensation through poincare hooks.** poincare's `RateLaw`
  passes each species' rate through the singledispatch function
  `compensate_volume(species, rhs, reaction_is_concentration)`. simbio
  registers an implementation for `Species`:

  - a concentration species fed by an amount reaction divides by the volume
    of its enclosing `Compartment`,
  - an amount species fed by a concentration reaction multiplies by it.

  `make_concentration` turns amount species into concentrations for
  `MassAction` rate laws. The enclosing compartment is found by walking
  `Node.parent` (`first_system_parent`).

- **Compartments.** `Compartment(System, abstract=True)` must declare
  **exactly one** `Volume`, checked in `__init_subclass__`. `Volume.__set_name__`
  stores the volume on its class as `_simbio_volume`. Species and volumes
  of a compartment cannot be linked to outside nodes. Only initial values
  can be passed in.

- **Reaction motifs** are ordinary poincare `System`s whose `Reactant`
  fields are combined into `MassAction` or `RateLaw`. Stoichiometry can be
  scaled from outside (`Synthesis(A=10 * A, ...)`).

- **SBML import** builds a class dynamically (`DynamicSystem` uses
  `System.__prepare__` and `type(name, (System,), namespace)`). It currently
  maps SBML species to plain poincare `Variable`s, not simbio `Species`
  (`from ... import Variable as Species  # TODO`). Unsupported SBML
  packages (`comp`, `fbc`, `groups`, `multi`, `qual`) raise
  `NotImplementedError`.

## Invariants and constraints

Verified:

- **Compartment models must match their plain-poincare equivalents.**
  `test_core.py` builds every amount/concentration × `RateLaw`/`AbsoluteRateLaw`/`MassAction`
  combination and checks it against a hand-written volume-scaled `System`.
  This includes time-varying volumes (`test_changing_volume`) and nested
  compartments. Any change to `core.py` must keep these equalities.
- **Exactly one `Volume` per `Compartment`. No external `Species` or
  `Volume` may be passed in** (`test_no_volume_in_compartment`,
  `test_more_than_one_volume_in_compartment`, `test_no_external_species_in_nested_compartment`).
- **Every reaction motif must instantiate and simulate** with all required
  arguments set to 1 (`reactions/test_reactions.py` discovers motifs
  automatically).
- **SBML semantic test suite:** `test_running` compares simulations with the
  reference results of the official SBML test suite 3.4.0. Known
  unsupported categories are `xfail`ed explicitly. Per-model absolute
  tolerance factors are in `io/sbml/tests/atol_factor.csv`.
- **MathML round-trips** (`io/mathML/test_mathML.py`).

Established conventions:

- New behaviour that depends on species type goes through poincare's
  singledispatch hooks, as in `core.py`, not through `isinstance` branches
  in poincare.
- New motifs follow `reactions/single.py`: give the reaction in the
  docstring (`A + B -> AB`), declare `Reactant` fields with
  `reaction_initial()` and rate `Parameter`s with `assign()`.

Unresolved (report, do not decide):

- Whether SBML species should become simbio `Species` inside `Compartment`s.
- `MichaelisMenten.to_eq_approx` / `to_qss_approx` raise `NotImplementedError`,
  and their intended semantics are only sketched in comments.
- `test_loading` swallows every exception, so it never fails. Loading
  errors only show up as `xfail("Loading error")` in `test_running`.

## Development environment and commands

The pixi manifest is in [pyproject.toml](pyproject.toml). These environments
install the **published** poincare and symbolite. If your change relies on
unreleased poincare or symbolite behaviour, test with source installs of
them and say so in your report.

```bash
pixi run test                                 # pytest --doctest-modules (default env)
pixi run -e test-py313 test                   # CI matrix: test-py312, test-py313 (with `io` extra)
pixi run test src/simbio/test_core.py         # subset
pixi run -e lint lint                         # `pre-commit run`: only *staged* files
pixi run -e lint pre-commit run --files <f>   # lint specific files
pixi run -e build build                       # runs `remotify` first, which REWRITES README.md links
```

- The first run of the SBML suite downloads the test-suite zip with `pooch`,
  so it needs network access. Later runs use the cache. That suite is the
  bulk of the roughly 2,400 tests and 1,400 xfails.
- Without `--all-files`, `pixi run -e lint lint` only checks staged files.
  The tree currently has about 45 ruff findings and 11 unformatted files.
  Fix only what you touch.
- Pyright is in the lint environment, but its pre-commit hook is commented
  out. No type check is enforced.
- Do not commit the README.md changes made by `build`/`remotify`.

Before calling a change done, run `pixi run test` and run ruff on the
changed files.

## Making changes

- **Compartment and volume logic:** edit `core.py`. Add a `test_core.py`
  case that compares against an explicitly volume-scaled plain `System`.
- **New motif:** add a `System` to the right `reactions/*.py` and export it
  in `reactions/__init__.py`. `test_reactions` picks it up. Add a
  quantitative test if its kinetics are not plain mass action.
- **SBML feature:** convert into `io/sbml/types.py` dataclasses in
  `from_libsbml.py`, then map them in `importer.SBMLImporter`. Check the
  affected test-suite cases. A case that changes from xfail to pass is the
  evidence that the feature works.
- **MathML:** keep `importer.py` and `exporter.py` symmetric and add round-trip cases.
- **Reaction primitives themselves** (`RateLaw`, `MassAction`, `Reactant`) live in
  `poincare/reactions/` in the poincare repository, not here.

## Testing and scientific correctness

- Prefer equivalence tests (compartment model against hand-scaled model),
  conservation checks (for example `A + AB` constant under binding) and
  analytic solutions over smoke tests.
- When results are not bit-identical, use relative tolerances as in
  `test_changing_volume` (1 %). Do not widen them without a reason.
- **Never** add or raise entries in `atol_factor.csv`, add `xfail`s, or
  broaden the exception filters in `test_sbml_test_suite.py` to make a
  regression pass. New entries need a model-specific justification that you
  report to the user.

## Ecosystem compatibility

- simbio depends on `poincare>=1.2.0` and uses its internals: `poincare._node.Node`/`NodeMapper`,
  `poincare.reactions.reactions.compensate_volume`/`make_concentration`, `poincare.types`,
  `poincare.compile.depends_on_at_least_one_variable_or_time`, `poincare.printing.latex`.
  If one of these looks wrong, fix it in poincare. Its AGENTS.md then
  requires running the simbio and jablonski suites against that change.
- It uses symbolite directly in `io/` (`Value`, `Name`, `ValueInfo`,
  `Call`, `translate.register`, `Unsupported`).
- jablonski does not depend on simbio. No package depends on simbio.

## Documentation and public API

- The public API is `simbio.__all__`, `simbio.reactions`, `simbio.io.sbml.load`/`loads`,
  `simbio.io.mathML` and `simbio.rebop`. Whatever is re-exported from
  poincare must stay importable from `simbio`.
- Document each motif's reaction scheme in its docstring, and state units
  and the amount/concentration semantics for new constructors.
- Update CHANGELOG.md, and the README when user-facing usage changes.

## Completion checklist

- [ ] Decided whether the change belongs in simbio or in poincare's reaction primitives.
- [ ] Compartment equivalence, the one-volume rule and the motif instantiation tests still pass.
- [ ] No tolerance factors, xfails or exception filters loosened in the SBML suite.
- [ ] `pixi run test` passes, and ruff is clean on the changed files.
- [ ] CHANGELOG.md updated, and unverified assumptions or SBML gaps reported to the user.
