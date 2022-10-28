# SimBio

`simbio` is a Python-based library of biological systems simulation.
As a comparison with other libraries we can enumerate:

- Models are composables,
  so you can create bigger models using smaller ones
- Models are python classes,
  so it is easier to understand the inners
  and easy to compose into bigger models
- Posibility to do `numba` JIT compilation
- Small footprint library,
  can be imported on a bigger application without fuzz

## Installation

If you are using pip,
it can be installed directly from PyPI:

```
pip install simbio
```

or the latest version from GitHub:

```
pip install git+https://github.com/hgrecco/simbio
```

## Examples

On the folder `src/simbio/tests/examples`,
we included some examples for the library usage.

## Development

We are using pytest for testing,
and pre-commit hooks to format and lint the codebase.

To easily set-up a development environment,
run the following commands:

```
git clone https://github.com/hgrecco/simbio
cd simbio
conda env create --file environment-dev.yml
pre-commit install
```

which assume you have git and conda preinstalled.
