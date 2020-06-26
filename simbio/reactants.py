"""
    simbio.reactants
    ~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import itertools as it
import math
from typing import Dict, Tuple


def _validate_state(k: str, site=None):
    if site is None:
        prefix = " State '{k}' "
    else:
        prefix = f"In {site}, state '{k}' "

    if "." in k:
        raise ValueError(f"{prefix} contains an invalid character: '.'")
    if "_" in k:
        raise ValueError(f"{prefix} contains an invalid character: '_'")
    if " " in k:
        raise ValueError(f"{prefix} contains an space, which is invalid")

    if not k[0].isalpha():
        raise ValueError(f"{prefix} does not start with an ascii letter")


class Reactant:
    """

    states
        ("", "p", "pp") - three states

        dict(Y416=("u", "p"), Y527=("u", "p")) - four states ("u_u", "u_p", "p_u", "p_p")

    Parameters
    ----------
    name
    concentration
    states
    """

    name: str

    # Site names
    _sites: Tuple[str, ...]

    # Maps site name to a tuple o sites
    _states_per_site: Dict[str, Tuple[str, ...]]

    # Maps state repr to state fraction
    _states_fractions: Dict[str, float]

    # Maps state repr to Reactant
    _states: Dict[str, "Reactant"]

    def __init__(
        self, name: str, concentration: float = 0, states=None, states_fractions=None
    ):
        self._name = name
        self._concentration = concentration

        if isinstance(states, str):
            states = tuple(states.split(" "))

        if states is None:
            self._sites = ()
            self._states_per_site = {}

        elif isinstance(states, tuple):
            for state in states:
                _validate_state(state)

            self._sites = ("s",)
            self._states_per_site = dict(s=states)

        elif isinstance(states, dict):
            self._sites = tuple(states.keys())

            self._states_per_site = {}
            for site, state_in_site in states.items():
                if isinstance(state_in_site, str):
                    state_in_site = tuple(state_in_site.split(" "))
                _validate_state(state_in_site, site)
                self._states_per_site[site] = state_in_site

        else:
            raise ValueError(f"Invalid type for states {type(states)}")

        if states_fractions is None:
            states_fractions = {}
            for ndx, el in enumerate(
                it.product(*tuple(self._states_per_site[k] for k in self._sites))
            ):
                state = "_".join(el)
                states_fractions[state] = 0.0 if ndx else 1.0

        if not math.isclose(sum(states_fractions.values()), 1):
            raise ValueError(f"In {name}, 'state_fractions' should add to 1.")

        # TODO Check that the keys are the same.
        self._states_fractions = states_fractions
        self._states = {}
        if self._sites:
            for el in it.product(*tuple(self._states_per_site[k] for k in self._sites)):
                state = "_".join(el)
                self._states[state] = Reactant(
                    name + "." + state,
                    concentration=states_fractions[state] * concentration,
                )

    @property
    def name(self):
        return self._name

    @property
    def concentration(self):
        return self._concentration

    @concentration.setter
    def concentration(self, value):
        self._concentration = value
        if not self.has_sites:
            return
        for k in self._sites:
            self._states[k].concentration = self._states_fractions[k] * value

    def _build_state_repr(self, vals):
        for k, v in vals.items():
            if k not in self._sites:
                raise ValueError(f"In {self.name}, {k} is not a valid site name")
            if v not in self._states_per_site[k]:
                raise ValueError(
                    f"In {self.name}, {v} is not a valid state for site {k}"
                )

        return "_".join(vals[k] for k in self._sites)

    @property
    def has_sites(self):
        return bool(self._sites)

    def __getattr__(self, item):
        if isinstance(item, str):
            if item in self._states:
                return self._states[item]
            raise ValueError(f"State {item} not found in {self.name}")
        elif isinstance(item, dict):
            return self._states[self._build_state_repr(item)]

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("Only floats and ints can multiply a Reactant")

        return InReactionReactant(self, other)

    __rmul__ = __mul__


class InReactionReactant:
    def __init__(self, reactant: Reactant, st_number=1):
        self.reactant = reactant
        self.st_number = st_number

    @property
    def name(self):
        return self.reactant.name

    @property
    def concentration(self):
        return self.reactant.concentration
