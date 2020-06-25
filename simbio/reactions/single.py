"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect
from typing import Callable, Generator, Tuple

import numpy as np
from simbio.reactants import InReactionReactant, Reactant

ODE_Fun = Callable[[float, np.ndarray, np.ndarray], None]


def _err_check(reactant_attrs, rhs_args):
    rhs_args = dict(rhs_args)
    try:
        rhs_args.pop("t")
    except KeyError:
        raise TypeError("_rhs must include t as the first argument.")

    names = tuple(rhs_args.keys())

    rhs_args = set(names)

    if reactant_attrs - rhs_args:
        raise TypeError(
            "_rhs arguments must include all Reactants but name, "
            "but %r not found." % (reactant_attrs - rhs_args)
        )

    if rhs_args - reactant_attrs:
        raise TypeError(
            "_rhs arguments must only include t and Reactants, "
            "but %r is not." % (rhs_args - reactant_attrs)
        )

    return names


class BaseReaction:
    """Base class of all single and compound reactions.

    The constructor automatically assign the kwargs to the attribute value.
    """

    _reactant_names: Tuple[str, ...] = ()
    st_numbers: np.ndarray

    def names(self) -> Tuple[str, ...]:
        """Return the name of the reactants in this reaction.
        """
        return tuple(getattr(self, attr).name for attr in self._reactant_names)

    def rhs(self, t: float, y: np.ndarray) -> np.ndarray:
        """Right hand side of the ODE, compatible with scipy.integrators
        """
        return np.asarray(self._rhs(t, *(y ** self.st_numbers)))

    def yield_ip_rhs(
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

    def _rhs(self, t, *args):
        """Right hand side of the ODE, compatible with scipy.integrators
        """
        raise NotImplementedError


class SingleReaction(BaseReaction):
    """Base class for all single reactions.
    """

    def __init__(self, **kwargs):
        if self.__class__ is SingleReaction:
            return

        rhs_args = inspect.signature(self._rhs).parameters
        reactant_attrs = set(
            k for k, v in self.__class__.__annotations__.items() if v is Reactant
        )

        self._reactant_names = _err_check(reactant_attrs, rhs_args)

        self.st_numbers = np.ones(len(self._reactant_names))

        while kwargs:
            key, value = kwargs.popitem()
            if key in self.__class__.__annotations__:
                if isinstance(value, InReactionReactant):
                    self.st_numbers[self._reactant_names.index(key)] = value.st_number
                    value = value.reactant
                setattr(self, key, value)
            else:
                raise ValueError(
                    f"{key} attribute not found in {self.__class__.__name__}"
                )

    def yield_ip_rhs(self, global_names=None):
        if global_names is None:

            def fun(t, y, out):
                out += self.rhs(t, y)

        else:
            pos = np.asarray(tuple(global_names.index(var) for var in self.names()))

            def fun(t, y, out):
                out[pos] += self.rhs(t, y[pos])

        yield fun


class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    A: Reactant
    B: Reactant

    rate: float

    def _rhs(self, t, A, B):
        return -self.rate * A, self.rate * A


class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    A: Reactant
    B: Reactant
    AB: Reactant

    rate: float

    def _rhs(self, t, A, B, AB):
        delta = self.rate * A * B
        return -delta, -delta, delta


class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    AB: Reactant
    A: Reactant
    B: Reactant

    rate: float

    def _rhs(self, t, AB, A, B):
        delta = self.rate * AB
        return -delta, delta, delta


class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    A: Reactant
    BC: Reactant
    AC: Reactant
    B: Reactant

    rate: float

    def _rhs(self, t, y):
        raise Exception("Not Implemented")
        return 0, 0, 0, 0


class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    AB: Reactant
    CD: Reactant
    AD: Reactant
    CB: Reactant

    rate: float

    def _rhs(self, t, y):
        raise Exception("Not Implemented")
        return 0, 0, 0, 0
