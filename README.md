# simbio
Library for simulation of biological systems


## Install notes
To install the package for developing:

```
> python -m venv .venv
> pip install -e .[full]
```

That will install all the needed packages to develop

## Run tests
For testing we are using [ward](https://wardpy.com/). To execute the tests use this command

```
> ward
```

## Run examples
On the folder `examples` we have exmaples for the library usage. These examples can be run with `ward` using this command

```
> ward --path examples
```