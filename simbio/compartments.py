"""
    simbio.compartments
    ~~~~~~~~~~~~~~~~~~~

    This module provides the definition for:
    - Compartment: contain reactants and reactions.
    - Universe: contain compartments, and reactions connecting the reactants within them.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from collections import defaultdict
from typing import Collection, Dict, List, Union

import numpy as np
from simbio.reactions.single import BaseReaction

from .parameters import Parameter
from .reactants import Reactant


def _removeprefix_or_none(name: str, cname: str):
    if name.startswith(cname + "."):
        return name[(len(cname) + 1) :]
    return None


class Compartment:
    """Contain reactants and reactions converting them.

    Parameters
    ----------
    name : str
        Name of the compartment.
    """

    #: Name of the compartment.
    name: str

    #: Mapping from reactant name to Reactant object.
    _reactants: Dict[str, Reactant]

    #: Mapping from parameter name to Parameter object.
    _parameters: Dict[str, Parameter]

    #: Reactions within this compartment.
    _reactions: List[BaseReaction]

    def __init__(self, name: str = "default"):
        self.name = name
        self._reactants = {}
        self._parameters = {}
        self._reactions = []

    def __getattr__(self, item):
        value = self._reactants.get(item) or self._parameters.get(item)
        if value is None:
            raise KeyError
        return value

    def get_reactant_by_fullname(self, fullname: str):
        """Obtain the a reactant or reactant state.

        The fullname can be:
            <reactant>
        or:
            <reactant name>.<state>

        Parameters
        ----------
        fullname : str

        Returns
        -------
        Reactant
        """
        if "." in fullname:
            reactant, state = fullname.split(".")
            return getattr(self._reactants[reactant], state)

        return self._reactants[fullname]

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
            reactant = Reactant(reactant, concentration=concentration)

        if reactant.name in self._reactions:
            raise ValueError(
                f"{reactant.name} already exists in compartment {self.name}"
            )

        self._reactants[reactant.name] = reactant

        return reactant

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
            parameter = Parameter(name=parameter, value=value)

        if parameter.name in self._parameters:
            raise ValueError(
                f"{parameter.name} already exists in compartment {self.name}"
            )

        self._parameters[parameter.name] = parameter

        return parameter

    def add_reaction(self, reaction: BaseReaction):
        self._reactions.append(reaction)

    def names(self):
        out = []

        # We do it like this instead of using a set to guarantee the order.
        for reaction in self._reactions:
            for name in reaction.names():
                if name not in out:
                    out.append(name)

        return tuple(out)

    def build_concentration_vector(self, concentrations=None):
        names = self.names()
        out = np.zeros(len(names))

        concentrations = concentrations or {}
        for ndx, name in enumerate(names):
            if name in concentrations:
                out[ndx] = concentrations[name]
            else:
                out[ndx] = self.get_reactant_by_fullname(name).concentration

        return out

    def yield_ip_rhs(self, global_names=None):
        for reaction in self._reactions:
            yield from reaction.yield_ip_rhs(global_names)

    def build_ip_rhs(self):

        funcs = tuple(self.yield_ip_rhs(self.names()))

        def fun(t, y):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, out)
            return out

        return fun

    def get_names_ndx(self, *names: Collection[str]):
        try:
            all_names = self.names()
            return tuple(all_names.index(name) for name in names)
        except ValueError as ex:
            raise ValueError("Reactant name not found in compartment: %s" % ex)


class Universe:
    def __init__(self):
        self._reactions: List[BaseReaction] = []
        self._compartments: Dict[str, Compartment] = {}

    def get_reactant_by_fullname(self, fullname):
        compartment, other = fullname.split(".", 1)
        return self._compartments[compartment].get_reactant_by_fullname(other)

    def add_compartment(self, compartment: Union[str, Compartment]) -> Compartment:
        if isinstance(compartment, str):
            compartment = Compartment(compartment)

        self._compartments[compartment.name] = compartment

        return compartment

    def add_reaction(self, reaction: BaseReaction):
        self._reactions.append(reaction)

    def names(self):
        out = []
        for cname, compartment in self._compartments.items():
            out.extend((cname + "." + name) for name in compartment.names())

        return tuple(out)

    def build_concentration_vector_nested(self, concentrations_by_compartment=None):
        names = self.names()
        out = np.zeros(len(names))

        ndx = 0
        concentrations_by_compartment = concentrations_by_compartment or {}
        for cname, compartment in self._compartments.items():
            cc = compartment.build_concentration_vector(
                concentrations_by_compartment.get(cname, {})
            )
            out[ndx : (ndx + len(cc))] = cc
            ndx += len(cc)

        return out

    def build_concentration_vector(self, concentrations_by_fullname=None):
        cnames = set(self._compartments.keys())
        d = defaultdict(dict)
        concentrations_by_fullname = concentrations_by_fullname or {}
        for key, value in concentrations_by_fullname.items():
            if "." not in key:
                raise ValueError(f"Compartment name not specified for: {key}")
            cname, rest = key.split(".", 1)
            if cname not in cnames:
                raise ValueError(f"Compartment name {cname} not in {cnames}")
            d[cname][rest] = value

        return self.build_concentration_vector_nested(d)

    def yield_ip_rhs(self, global_names=None):

        for cname, compartment in self._compartments.items():
            vnames = tuple(_removeprefix_or_none(name, cname) for name in global_names)
            yield from compartment.yield_ip_rhs(vnames)

        for reaction in self._reactions:
            yield from reaction.yield_ip_rhs(global_names)

    def build_ip_rhs(self):

        funcs = tuple(self.yield_ip_rhs(self.names()))

        def fun(t, y):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, out)
            return out

        return fun

    def get_names_ndx(self, *names: Collection[str]) -> np.ndarray:
        out = []
        all_names = self.names()
        try:
            for name in names:
                out.append(all_names.index(name))
        except ValueError:
            raise ValueError(f"Reactant name {name} not found in universe: {all_names}")

        return np.asarray(out, dtype=np.int)
