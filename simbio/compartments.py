"""
    simbio.compartments
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain
from typing import Dict, List, Tuple, Union

import numpy as np

from .core import Container
from .parameters import Parameter
from .reactants import Reactant
from .reactions.single import BaseReaction


@dataclass(repr=False)
class Compartment(Container):
    __reactions: List[BaseReaction] = field(default_factory=list, repr=False)

    @property
    def compartments(self) -> Tuple[Compartment, ...]:
        return self.filter_contents(Compartment)

    @property
    def reactants(self) -> Tuple[Reactant, ...]:
        return self.filter_contents(Reactant)

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        return self.filter_contents(Parameter)

    @property
    def reactions(self) -> Tuple[BaseReaction, ...]:
        out = list(self.__reactions)
        for compartment in self.compartments:
            out.extend(compartment.reactions)
        return tuple(out)

    def add_reaction(self, reaction: BaseReaction):
        if not isinstance(reaction, BaseReaction):
            raise TypeError(f"{reaction} is not a Reaction.")

        out = [r for r in reaction.reactants if r not in self]
        if out:
            raise Exception(
                "Some reactants are outside this compartment: %s", [r.name for r in out]
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
        return self.add(compartment)

    def add_reactant(self, reactant: Union[str, Reactant], concentration=0) -> Reactant:
        """Add reactant to this compartment.

        If the reactant is a string, a Reactant object will be automatically created.

        Parameters
        ----------
        reactant : str or Reactant
        concentration : float

        Returns
        -------
        reactant
        """
        if isinstance(reactant, str):
            reactant = Reactant(
                name=reactant, belongs_to=self, concentration=concentration
            )
        return self.add(reactant)

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
        return self.add(parameter)

    def copy(self, name: str = None, belongs_to: Container = None) -> Compartment:
        # __contents copy is handled by Container.copy
        new = super().copy(name=name, belongs_to=belongs_to)

        # We have to handle __reactions copy
        # For each reaction, we get the relative names of its reactants
        # and parameters, which will be the same in the new Compartment.
        # Then we instantiate another reaction searching corresponding
        # reactants and parameters from the new compartment.
        for reaction in self.__reactions:
            kwargs = {}

            for name, reactant, st_number in zip(
                reaction._reactant_names, reaction.reactants, reaction.st_numbers
            ):
                rel_name = self.relative_name(reactant)
                kwargs[name] = st_number * new[rel_name]

            for name, parameter in zip(reaction._parameter_names, reaction.parameters):
                rel_name = self.relative_name(parameter)
                kwargs[name] = new[rel_name]

            new.add_reaction(reaction.__class__(**kwargs))
        return new

    @property
    def in_reaction_reactants(self) -> Tuple[Reactant, ...]:
        out = {}  # Using dict as an ordered set.
        for reaction in self.reactions:
            for reactant in reaction.reactants:
                out[reactant] = 1
        return tuple(out.keys())

    @property
    def in_reaction_parameters(self) -> Tuple[Parameter, ...]:
        out = {}  # Using dict as an ordered set.
        for reaction in self.reactions:
            for parameter in reaction.parameters:
                out[parameter] = 1
        return tuple(out.keys())

    @property
    def in_reaction_rectant_names(self) -> Tuple[str, ...]:
        return tuple(map(self.relative_name, self.in_reaction_reactants))

    def build_concentration_vector(self, concentrations=None):
        if concentrations is None:
            concentrations = {}
        names = self.in_reaction_rectant_names
        out = np.zeros(len(names))
        for i, name in enumerate(names):
            out[i] = concentrations.get(name) or self[name].concentration
        # TODO: Raise warning for unused concentrations?
        return out

    def build_parameters(self, parameters=None) -> Dict[Parameter, float]:
        if parameters is None:
            parameters = {}

        out = {}
        for p in self.in_reaction_parameters:
            out[p] = parameters.pop(p.name, p.value)

        if len(parameters) > 0:
            raise ValueError("Some parameters were not used:", parameters)

        return out

    def build_ip_rhs(self, parameters=None):
        reactants = self.in_reaction_reactants
        parameters = self.build_parameters(parameters)
        funcs = (r.yield_ip_rhs(reactants, parameters) for r in self.reactions)
        funcs = tuple(chain.from_iterable(funcs))

        def fun(t, y):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, out)
            return out

        return fun


class Universe(Compartment):
    """Universe is a Compartment that belongs to None."""

    def __init__(self, name: str, belongs_to=None):
        super().__init__(name=name, belongs_to=belongs_to)
