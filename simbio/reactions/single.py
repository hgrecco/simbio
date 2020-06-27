"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect
from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict, Generator, Tuple

import numpy as np
from simbio.parameters import Parameter
from simbio.reactants import InReactionReactant, Reactant

ODE_Fun = Callable[[float, np.ndarray, np.ndarray], None]


class BaseReaction:
    """Base class of all single and compound reactions.

    The constructor automatically assign the kwargs to the attribute value.
    """

    _reactant_names: Tuple[str, ...] = ()
    _parameter_names: Tuple[str, ...] = ()
    st_numbers: np.ndarray

    def names(self) -> Tuple[str, ...]:
        """Return the name of the reactants in this reaction.
        """
        return tuple(getattr(self, attr).name for attr in self._reactant_names)

    @property
    def parameters(self) -> Dict[str, float]:
        return {name: getattr(self, name).value for name in self._parameter_names}

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


class SingleReaction(BaseReaction):
    """Base class for all single reactions.
    """

    def __init_subclass__(cls, **kwargs):
        """Initialize class from rhs method.

        Check if rhs method is well-defined. It must:
        - be a staticmethod
        - have an ordered signature (t, *Reactants, *Parameters)

        Set class annotations from rhs, and create init and others with dataclass.
        Set (ordered) tuples of reactions and parameters names.
        """

        # Check if staticmethod
        if not isinstance(inspect.getattr_static(cls, "rhs"), staticmethod):
            raise TypeError(
                f"{cls.__name__}.rhs must be a staticmethod. Use @staticmethod decorator."
            )

        # Check signature order
        rhs_params = iter(inspect.signature(cls.rhs).parameters.values())

        v = next(rhs_params)
        if not v.name == "t":
            raise TypeError(
                f"{cls.__name__}.rhs first parameter is {v.name}, but must be t"
            )

        for v in rhs_params:
            if issubclass(v.annotation, Reactant):
                continue
            elif issubclass(v.annotation, Parameter):
                break
            else:
                raise TypeError(
                    f"{cls.__name__}.rhs parameter {v.name} is neither Reactant nor Parameter"
                )

        for v in rhs_params:
            if issubclass(v.annotation, Reactant):
                raise TypeError(
                    f"{cls.__name__}.rhs are in the wrong order. Reactant {v.name} found after Parameter."
                )
            elif not issubclass(v.annotation, Parameter):
                raise TypeError(
                    f"{cls.__name__}.rhs parameter {v.name} is not Parameter"
                )

        # Set class annotations from rhs
        rhs_annotations = cls.rhs.__annotations__
        if "t" in rhs_annotations:
            rhs_annotations.pop("t")
        setattr(cls, "__annotations__", rhs_annotations)

        # Save tuples of names
        cls._reactant_names = tuple(
            k for k, v in rhs_annotations.items() if issubclass(v, Reactant)
        )
        cls._parameter_names = tuple(
            k for k, v in rhs_annotations.items() if issubclass(v, Parameter)
        )

        return dataclass(cls)

    def __post_init__(self):
        if self.__class__ is SingleReaction:
            return

        self.st_numbers = np.ones(len(self._reactant_names))

        for i, key in enumerate(self._reactant_names):
            value = getattr(self, key)

            if isinstance(value, InReactionReactant):
                self.st_numbers[i] = value.st_number
                value = value.reactant
                setattr(self, key, value)

            if isinstance(value, Reactant) and value.has_sites:
                raise ValueError(
                    f"The state of {value.name} must be specified to link a this reaction."
                )

    def build_rhs(self) -> Callable:
        """Right hand side of the ODE, compatible with scipy.integrators"""
        return partial(self.rhs, **self.parameters)

    def yield_ip_rhs(self, global_names=None):
        if global_names is None:
            pos = slice()
        else:
            pos = np.asarray(tuple(global_names.index(var) for var in self.names()))

        def fun(t, y, out):
            out[pos] += self.build_rhs()(t, *(y[pos] ** self.st_numbers))

        yield fun

    @staticmethod
    def rhs(t, *args):
        raise NotImplementedError


class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    @staticmethod
    def rhs(t, A: Reactant, B: Reactant, rate: Parameter):
        delta = rate * A
        return -delta, delta


class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    @staticmethod
    def rhs(t, A: Reactant, B: Reactant, AB: Reactant, rate: Parameter):
        delta = rate * A * B
        return -delta, -delta, delta


class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    @staticmethod
    def rhs(t, AB: Reactant, A: Reactant, B: Reactant, rate: Parameter):
        delta = rate * AB
        return -delta, delta, delta


class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    @staticmethod
    def rhs(t, A: Reactant, BC: Reactant, AC: Reactant, B: Reactant, rate: Parameter):
        raise NotImplementedError


class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    @staticmethod
    def rhs(t, AB: Reactant, CD: Reactant, AD: Reactant, CB: Reactant, rate: Parameter):
        raise NotImplementedError
