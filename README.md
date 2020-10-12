# simbio
`simbio` is a Python-based library of biological systems simulation. As a comparison with other libraries we can enumerate:

- Models are composables, so you can create bigger models using smaller ones
- Models are python classes, so it is easier to understand the inners and easy to compose into bigger models
- Posibility to do `numba` JIT compilation
- Small footprint library, can be imported on a bigger application without fuzz

## Install notes
To install the package for developing:

```
> python -m venv .venv
> pip install -e .[full]
```

That will install all the needed packages to develop and the pre-commit hooks.

## Run tests
For testing we are using [ward](https://wardpy.com/). To execute the tests use this command

```
> ward
```

## Run examples
On the folder `examples` we have examaples for the library usage

```
> python examples/<example>.py
```

## pre-commits
We have in place pre-commit hooks, to have a common style. We use

- black
- flake8
- isort

They can be executed, without any commit, with

```
> pre-commit run --all-files
```
