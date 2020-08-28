from dataclasses import dataclass, field
from string import Template
from typing import Callable, Generator, Tuple, get_type_hints

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

    _species_names: Tuple[str, ...] = field(init=False)
    _parameter_names: Tuple[str, ...] = field(init=False)
    st_numbers: np.ndarray = field(init=False)

    def __init_subclass__(cls):
        """Initialize class as a dataclass.

        Set (ordered) tuples of reactions and parameters names from __init__ annotations.
        """
        dataclass(cls)

        # Save tuples of names
        annotations = get_type_hints(cls.__init__)
        del annotations["return"]
        cls._species_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Species)
        )
        cls._parameter_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Parameter)
        )

    def __post_init__(self):
        """Initializes and validates arguments.

        Validates that instance arguments are Species and Parameters.
        Unpacks InReactionSpecies, saving the st_number.
        """
        self.st_numbers = np.ones(len(self._species_names))

        # Validate expected Species
        for i, (key, value) in enumerate(zip(self._species_names, self.species)):
            if isinstance(value, InReactionSpecies):
                self.st_numbers[i] = value.st_number
                setattr(self, key, value.species)
            elif not isinstance(value, Species):
                raise TypeError(f"{value} is not a Species.")

        # Validate expected Parameters
        for parameter in self.parameters:
            if not isinstance(parameter, Parameter):
                raise TypeError(f"{parameter} is not a Parameter.")

    @property
    def species(self) -> Tuple[Species, ...]:
        """Return a tuple of the species in this reaction."""
        return tuple(getattr(self, name) for name in self._species_names)

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        """Return a tuple of the parameters in this reaction."""
        return tuple(getattr(self, name) for name in self._parameter_names)

    def _yield_ip_rhs(
        self,
        global_species: Tuple[Species, ...] = None,
        global_parameters: Tuple[Parameter, ...] = None,
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
