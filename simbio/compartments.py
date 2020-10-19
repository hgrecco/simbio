"""
    simbio.compartments
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import chain
from typing import Dict, List, Tuple, Union

import numpy as np
from orderedset import OrderedSet

from .core import Container, Content
from .parameters import BaseParameter, Parameter
from .reactions.single import BaseReaction
from .species import Species


class DuplicateComponentError(Exception):
    pass


class DuplicateContentDict(dict):
    """For Model.__prepare__.

    On class body parsing, it saves Content (Species, Parameters and Compartments)
    on a separate dict, recording duplicates. Additionally, sets Content._name.
    Being on a separate dict, they are not added to the class __dict__.
    """

    def __init__(self):
        self.contents = defaultdict(list)

    def __setitem__(self, k, v):
        if isinstance(v, Content):
            v._name = k
            self.contents[k].append(v)
        else:
            super().__setitem__(k, v)

    # Override update and __ior__, which bypass __setitem__.
    def update(self, *args, **kwargs):
        raise NotImplementedError

    def __ior__(self, other):
        raise NotImplementedError


class Model(Container, type):
    __reactions: OrderedSet[BaseReaction]

    def copy(self) -> Model:
        return self.__class__(self.name, (self,), DuplicateContentDict())

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name == other.name) and (self._contents == other._contents)

    def __call__(cls, *, name=""):
        if cls not in (Model, Compartment):
            raise TypeError(f"{cls} is not callable.")

        args = name, (), DuplicateContentDict()
        self = cls.__class__.__new__(cls.__class__, *args)
        self.__class__.__init__(self, *args)
        return self

    def __prepare__(cls, name):
        return DuplicateContentDict()

    def __init__(self, name, bases, clsdict):
        super().__init__(name, bases, clsdict, name=name or None)

        # Copy inherited components and reactions
        # from _contents and _reactions respectively,
        # since they may have been added dynamically.

        # Check for:
        # 1. Duplicate new components in class body definition.
        # 2. Colliding inherited components that must be overriden.
        # 3. Collisions between inherited and new components, which
        # aren't marked as overriding.
        contents = clsdict.contents

        duplicates = {k for k, v in contents.items() if len(v) > 1}
        if duplicates:
            raise DuplicateComponentError(
                f"Duplicate Components found in {self} definition:", duplicates
            )

        for base in bases:
            for k, v in base._contents.items():
                contents[k].append(v)

        to_override = []
        for k, (v0, *v) in contents.items():

            if not all(isinstance(vi, v0.__class__) for vi in v):  # Mixing classes
                raise TypeError

            if v0.parent is None:  # Not inherited
                if len(v) == 0:  # No collision
                    self._add(v0)
                elif isinstance(v0, BaseParameter) and v0.override:
                    self._add(v0)
                elif isinstance(v0, Model) and all(issubclass(v0, vi) for vi in v):
                    self._add(v0)
                else:
                    to_override.append(k)

            else:  # Inherited
                if all(vi == v0 for vi in v):
                    self._add(v0.copy())
                else:
                    to_override.append(k)

        if to_override:
            raise DuplicateComponentError(
                "Multiple inherited Species must be overriden:", to_override
            )

        # For each reaction, we get the relative names of its species
        # and parameters, which will be the same in the new Compartment.
        # Then we instantiate another reaction searching corresponding
        # species and parameters from the new compartment.
        self.__reactions = OrderedSet()
        for base in bases:
            for reaction in base.reactions:
                kwargs = {}

                for name, species, st_number in zip(
                    reaction._species_names, reaction.species, reaction.st_numbers
                ):
                    rel_name = base._relative_name(species)
                    kwargs[name] = st_number * self[rel_name]

                for name, parameter in zip(
                    reaction._parameter_names, reaction.parameters
                ):
                    rel_name = base._relative_name(parameter)
                    kwargs[name] = self[rel_name]

                self.add_reaction(reaction.__class__(**kwargs))

    # Model view components
    # =====================
    @property
    def compartments(self) -> Tuple[Compartment, ...]:
        return self._filter_contents(Model)

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

    # Model add components
    # ====================
    def add_reaction(self, reaction: BaseReaction, *, override=False):
        if not isinstance(reaction, BaseReaction):
            raise TypeError(f"{reaction} is not a Reaction.")

        # We only test for the first common parent of Species, not Parameters,
        # since reaction equivalence is given by its Species. Otherwise,
        # an equivalent reaction with different parameters might be duplicated
        # in a different Compartment, at a different level.
        common_parent = Content._common_parent(*reaction.species)
        if common_parent is not self:
            raise Exception(
                "The reaction must be added to the first common parent Compartment of its Species:",
                common_parent,
            )

        # But its Parameters must be accesible from this Compartment.
        outside_parameters = [p for p in reaction.parameters if p not in self]
        if outside_parameters:
            raise Exception(
                "The reaction parameters must belong to this Compartment or any subcompartments. Parameters outside this Compartment are:",
                outside_parameters,
            )

        if reaction in self.__reactions:
            if not override:
                raise Exception(
                    "There's an existent equivalent reaction. To override it, use override=True."
                )
        self.__reactions.add(reaction)
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
            compartment = Compartment(name=compartment)
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
            species = Species(value, name=species)
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
            parameter = Parameter(value, name=parameter)
        return self._add(parameter)

    # Model build RHS
    # ===============
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

    def _resolve_values(
        self, values: Dict[Union[str, Species, Parameter], float] = None
    ) -> Tuple[Dict, List]:
        out, unexpected = {}, []
        for name, value in values.items():
            if isinstance(name, str):
                try:
                    name = self[name]
                    out[name] = value
                except (KeyError, TypeError):
                    unexpected.append(name)
            elif isinstance(name, BaseParameter):
                if name not in self:
                    unexpected.append(name)
                else:
                    out[name] = value
            else:
                unexpected.append(name)
        return out, unexpected

    def _build_value_vectors(
        self,
        values: Dict[Union[str, Species, Parameter], float] = None,
        raise_on_unexpected: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        if values is None:
            values = {}
        else:
            values, unexpected = self._resolve_values(values)

            if raise_on_unexpected and unexpected:
                raise ValueError(
                    f"Received unexpected values not found in Compartment: {unexpected}"
                )

        species = self._in_reaction_species
        species = np.fromiter(
            (values.get(r, r.value) for r in species), dtype=float, count=len(species)
        )

        parameters = self._in_reaction_parameters
        parameters = np.fromiter(
            (values.get(r, r.value) for r in parameters),
            dtype=float,
            count=len(parameters),
        )
        return species, parameters

    def _build_ip_rhs(self):
        species, parameters = self._in_reaction_species, self._in_reaction_parameters
        funcs = (r._yield_ip_rhs(species, parameters) for r in self.reactions)
        funcs = tuple(chain.from_iterable(funcs))

        def fun(t, y, p):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, p, out)
            return out

        return fun


class Compartment(metaclass=Model):
    pass
