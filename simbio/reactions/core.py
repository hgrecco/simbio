from dataclasses import dataclass
from string import Template
from typing import Callable, Generator, Tuple, get_type_hints

import numpy as np
from sympy import Derivative, Equality, symbols

from ..parameters import Parameter
from ..species import InReactionSpecies, Species

ODE_Fun = Callable[[float, np.ndarray, np.ndarray], None]


class BaseReaction:
    """Base class of all single and compound reactions."""

    # Class attributes
    _species_names: Tuple[str, ...]
    _parameter_names: Tuple[str, ...]
    _equivalent_species: Tuple[Tuple[str, ...], ...]

    # Instance attributes
    st_numbers: np.ndarray

    def __init_subclass__(cls):
        """Initialize class as a dataclass.

        Set (ordered) tuples of reactions and parameters names from __init__ annotations.
        """
        # Copy eq and hash methods
        # @dataclass would override them if not called with @dataclass(eq=False)
        cls.__eq__ = cls.__eq__
        cls.__hash__ = cls.__hash__

        # Create __init__ with dataclass after copying eq and hash
        dataclass(cls)

        # Save tuples of names inspecting __init__
        # If we inspect the class directly, we have to remove other unrelated annotations.
        annotations = get_type_hints(cls.__init__)
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

    @property
    def equivalent_species(self) -> Tuple[Tuple[Species, ...], ...]:
        """Return tuples of equivalent species in this reaction."""
        return tuple(
            tuple(getattr(self, s) for s in S) for S in self._equivalent_species
        )

    def __hash__(self) -> int:
        # Replace each species by its hash,
        # sort each equivalent group by hash,
        # and hash the resulting tuple of tuples.
        sorted_groups = (tuple(sorted(map(hash, s))) for s in self.equivalent_species)
        return hash(tuple(sorted_groups))

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return hash(other) == hash(self)

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
