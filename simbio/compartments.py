"""
    simbio.compartments
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import field
from itertools import chain
from typing import Dict, List, Tuple, Union

import numpy as np

from .core import Container
from .parameters import Parameter
from .reactions.single import BaseReaction
from .species import Species


class Compartment(Container):
    __reactions: List[BaseReaction] = field(
        default_factory=list, init=False, repr=False
    )

    @property
    def compartments(self) -> Tuple[Compartment, ...]:
        return self._filter_contents(Compartment)

    @property
    def species(self) -> Tuple[Species, ...]:
        return self._filter_contents(Species)

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        return self._filter_contents(Parameter)

    @property
    def reactions(self) -> Tuple[BaseReaction, ...]:
        out = list(self.__reactions)
        for compartment in self.compartments:
            out.extend(compartment.reactions)
        return tuple(out)

    def add_reaction(self, reaction: BaseReaction):
        if not isinstance(reaction, BaseReaction):
            raise TypeError(f"{reaction} is not a Reaction.")

        components = chain(reaction.species, reaction.parameters)
        out = [c for c in components if c not in self]
        if out:
            raise Exception(
                "Some components are outside this compartment: %s",
                [c.name for c in out],
            )
        self.__reactions.append(reaction)
        return reaction

    def add_compartment(self, compartment: Union[str, Compartment]) -> Compartment:
        """Add compartment to this compartment.

        If compartment is a string, a Compartment object will be automatically created.

        Parameters
        ----------
        compartment : str or Compartment

        Returns
        -------
        comparment
        """
        if isinstance(compartment, str):
            compartment = Compartment(name=compartment, belongs_to=self)
        return self._add(compartment)

    def add_species(self, species: Union[str, Species], value=0) -> Species:
        """Add species to this compartment.

        If the species is a string, a Species object will be automatically created.

        Parameters
        ----------
        species : str or Species
        value : float

        Returns
        -------
        species
        """
        if isinstance(species, str):
            species = Species(name=species, belongs_to=self, value=value)
        return self._add(species)

    def add_parameter(self, parameter: Union[str, Parameter], value=0) -> Parameter:
        """Add parameter to this compartment.

        If the parameter is a string, a Parameter object will be automatically created.

        Parameters
        ----------
        parameter : str or Parameter
        value : float

        Returns
        -------
        parameter
        """
        if isinstance(parameter, str):
            parameter = Parameter(name=parameter, belongs_to=self, value=value)
        return self._add(parameter)

    def copy(self, name: str = None, belongs_to: Container = None) -> Compartment:
        # __contents copy is handled by Container.copy
        new = super().copy(name=name, belongs_to=belongs_to)

        # We have to handle __reactions copy
        # For each reaction, we get the relative names of its species
        # and parameters, which will be the same in the new Compartment.
        # Then we instantiate another reaction searching corresponding
        # species and parameters from the new compartment.
        for reaction in self.__reactions:
            kwargs = {}

            for name, species, st_number in zip(
                reaction._species_names, reaction.species, reaction.st_numbers
            ):
                rel_name = self._relative_name(species)
                kwargs[name] = st_number * new[rel_name]

            for name, parameter in zip(reaction._parameter_names, reaction.parameters):
                rel_name = self._relative_name(parameter)
                kwargs[name] = new[rel_name]

            new.add_reaction(reaction.__class__(**kwargs))
        return new

    @property
    def _in_reaction_species(self) -> Tuple[Species, ...]:
        out = {}  # Using dict as an ordered set.
        for reaction in self.reactions:
            for species in reaction.species:
                out[species] = 1
        return tuple(out.keys())

    @property
    def _in_reaction_parameters(self) -> Tuple[Parameter, ...]:
        out = {}  # Using dict as an ordered set.
        for reaction in self.reactions:
            for parameter in reaction.parameters:
                out[parameter] = 1
        return tuple(out.keys())

    @property
    def _in_reaction_species_names(self) -> Tuple[str, ...]:
        return tuple(map(self._relative_name, self._in_reaction_species))

    @property
    def _in_reaction_parameter_names(self) -> Tuple[str, ...]:
        return tuple(map(self._relative_name, self._in_reaction_parameters))

    def _build_concentration_vector(
        self, concentrations: Dict[Union[str, Species], float] = None
    ) -> np.ndarray:

        species = self._in_reaction_species
        out = np.fromiter((r.value for r in species), dtype=float, count=len(species))

        if concentrations is not None:
            for sp, concentration in concentrations.items():
                if isinstance(sp, str):
                    sp = self[sp]
                out[species.index(sp)] = concentration

        return out

    def _build_parameter_vector(
        self, parameters: Dict[Union[str, Parameter], float] = None
    ) -> np.ndarray:

        _parameters = self._in_reaction_parameters
        out = np.fromiter(
            (r.value for r in _parameters), dtype=float, count=len(_parameters)
        )

        if parameters is not None:
            for parameter, value in parameters.items():
                if isinstance(parameter, str):
                    parameter = self[parameter]
                out[_parameters.index(parameter)] = value

        return out

    def _build_ip_rhs(self):
        species = self._in_reaction_species
        parameters = self._in_reaction_parameters
        funcs = (r._yield_ip_rhs(species, parameters) for r in self.reactions)
        funcs = tuple(chain.from_iterable(funcs))

        def fun(t, y, p):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, p, out)
            return out

        return fun


class Universe(Compartment):
    """Universe is a Compartment that belongs to None."""

    def __init__(self, name: str, belongs_to=None):
        super().__init__(name=name, belongs_to=belongs_to)
