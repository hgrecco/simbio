# SimBio
`simbio` is a Python-based library of biological systems simulation. As a comparison with other libraries we can enumerate:

- Models are composables, so you can create bigger models using smaller ones
- Models are python classes, so it is easier to understand the inners and easy to compose into bigger models
- Posibility to do `numba` JIT compilation
- Small footprint library, can be imported on a bigger application without fuzz

## Installation
The package is not yet available at PyPI. To install the package, clone or download the repository. Or, if you're using pip:

```
> pip install git+https://github.com/hgrecco/simbio
```

## Examples
On the folder `examples`, we included several examples for the library usage. Run them with:

```
> python examples/<example>.py
```

## Developers

### Installation notes
To install the package for development, use the [dev] option.

It's recommended to create a virtual environment first:

```
> python -m venv .venv
```

or, if using conda,

```
> conda create -n simbio python
> conda activate simbio
```

Then, after cloning the repository, install with:

```
> pip install -e .[dev]
```

which includes all the needed packages to develop.

### pre-commit
We have in place pre-commit hooks, to have a common style. We use

- black
- flake8
- isort

They can be executed, without any commit, with

```
> pre-commit run --all-files
```

or installed to run before each commit with:

```
> pre-commit install
```

### Running tests
For testing, we are using [ward](https://wardpy.com/). To execute the tests use this command

```
> ward
```
