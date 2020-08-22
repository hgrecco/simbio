import inspect
from dataclasses import dataclass
from string import Template
from typing import Callable, Generator, Tuple

import numpy as np

from ..parameters import Parameter
from ..species import InReactionSpecies, Species

try:
    from sympy import symbols, Derivative, Equality
except ImportError:

    def symbols(*args, **kwargs):
        raise Exception(
            "This function requires sympy. Please install it:\n"
            "\tpip install sympy\n"
            "\t\t\tor\n"
            "\tconda install sympy\n"
        )

    Derivative = Equality = symbols

ODE_Fun = Callable[[float, np.ndarray, np.ndarray], None]


class BaseReaction:
    """Base class of all single and compound reactions."""

    _species_names: Tuple[str, ...]
    _parameter_names: Tuple[str, ...]
    st_numbers: np.ndarray

    def __init_subclass__(cls, annotations: dict = None):
        """Initialize class from annotations dict.

        Set class annotations, then create init and others with dataclass.
        Set (ordered) tuples of reactions and parameters names.
        """
        if annotations is None:
            return cls

        setattr(cls, "__annotations__", annotations)

        # Save tuples of names
        cls._species_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Species)
        )
        cls._parameter_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Parameter)
        )

        return dataclass(cls)

    def __post_init__(self):
        """Initializes and validates arguments.

        Validates that instance arguments are Species and Parameters.
        Unpacks InReactionSpecies, saving the st_number.
        """
        self.st_numbers = np.ones(len(self._species_names))

        # Validate expected Species
        for i, key in enumerate(self._species_names):
            value = getattr(self, key)

            if isinstance(value, InReactionSpecies):
                self.st_numbers[i] = value.st_number
                setattr(self, key, value.species)
            elif not isinstance(value, Species):
                raise TypeError(f"{value} is not a Species.")

        # Validate expected Parameters
        for key in self._parameter_names:
            value = getattr(self, key)
            if not isinstance(value, Parameter):
                raise TypeError(f"{value} is not a Parameter.")

    @property
    def species(self) -> Tuple[Species, ...]:
        """Return a tuple of the species in this reaction."""
        return tuple(getattr(self, name) for name in self._species_names)

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        """Return a tuple of the parameters in this reaction."""
        return tuple(getattr(self, name) for name in self._parameter_names)

    def _yield_ip_rhs(
        self, global_names: Tuple[str, ...]
    ) -> Generator[ODE_Fun, None, None]:
        """Yield one or many functions representing the right hand side of the ODE equation.

        The arguments of these functions are:
            t: float, the time
            y: ndarray, the input vector
            out: ndarray, the calculated rhs of the equation which is modified inplace.

        Applying all functions sequentially it is posiblle
        """
        raise NotImplementedError

    # Latex
    def _yield_using_template(self, tmpls, *, use_brackets=True):
        for tmpl in tmpls:
            yield self._template_replace(tmpl, use_brackets=use_brackets)

    def _template_replace(self, tmpl, *, use_brackets=True):
        if use_brackets:
            c = "[%s]"
        else:
            c = "%s"
        return Template(tmpl).substitute(
            **{name: c % getattr(self, name).name for name in self._species_names},
            **{name: getattr(self, name).name for name in self._parameter_names},
        )

    def yield_latex_equations(self, *, use_brackets=True):
        t = symbols("t")
        species = self.species
        if use_brackets:
            species = (f"[{x}]" for x in species)
        species = tuple(map(symbols, species))
        parameters = map(symbols, self.parameters)

        for lhs, rhs in zip(species, self.rhs(t, *species, *parameters)):
            yield Equality(Derivative(lhs, t), rhs)

    def yield_latex_reaction(self):
        # Use \usepackage{mhchem}
        raise NotImplementedError

    def yield_latex_species_values(self):
        raise NotImplementedError

    def yield_latex_parameter_values(self):
        raise NotImplementedError


def _check_signature(method, t_first: bool):
    """Validates type and order of signature arguments.

    Signature should be (t, *Species, *Parameter)

    Parameters
    ----------
    t_first : bool
        True if "t" should be the first parameter.
    """
    params = iter(inspect.signature(method).parameters.values())

    if t_first:
        v = next(params)
        if not v.name == "t":
            raise TypeError(f"{method} first parameter is {v.name}, but must be t")

    for v in params:
        if issubclass(v.annotation, Species):
            continue
        elif issubclass(v.annotation, Parameter):
            break
        else:
            raise TypeError(
                f"{method} parameter {v.name} is neither Species nor Parameter"
            )

    for v in params:
        if issubclass(v.annotation, Species):
            raise TypeError(
                f"{method} are in the wrong order. Species {v.name} found after Parameter."
            )
        elif not issubclass(v.annotation, Parameter):
            raise TypeError(f"{method} parameter {v.name} is not Parameter")
