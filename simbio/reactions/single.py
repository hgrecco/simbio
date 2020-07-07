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
from string import Template
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

    def _yield_using_template(self, tmpls, *, use_brackets=True):
        for tmpl in tmpls:
            yield self._template_replace(tmpl, use_brackets=use_brackets)

    def _template_replace(self, tmpl, *, use_brackets=True):
        if use_brackets:
            c = "[%s]"
        else:
            c = "%s"
        return Template(tmpl).substitute(
            **{name: c % getattr(self, name).name for name in self._reactant_names},
            **{name: getattr(self, name).name for name in self._parameter_names},
        )

    def yield_latex_equations(self, *, use_brackets=True):
        raise NotImplementedError

    def yield_latex_reaction(self):
        # Use \usepackage{mhchem}
        raise NotImplementedError

    def yield_latex_reactant_values(self):
        raise NotImplementedError

    def yield_latex_parameter_values(self):
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

    def yield_latex_reactant_values(self, column_separator="&"):
        for name in self._reactant_names:
            yield getattr(self, name).name
            yield column_separator
            yield getattr(self, name).value

    def yield_latex_parameter_values(self, column_separator="&"):
        for name in self._parameter_names:
            yield getattr(self, name).name
            yield column_separator
            yield getattr(self, name).value


class Creation(SingleReaction):
    """A substance is created from nothing.

      -> A
    """

    @staticmethod
    def rhs(t, A: Reactant, rate: Parameter):
        return rate * A

    def yield_latex_equations(self, *, use_brackets=True):
        yield from self._yield_using_template(
            (r"\frac{d$A}{dt} = $rate $A",), use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ \varnothing ->[$rate] $A }")


class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A ->
    """

    @staticmethod
    def rhs(t, A: Reactant, rate: Parameter):
        return -rate * A

    def yield_latex_equations(self, *, use_brackets=True):
        yield from self._yield_using_template(
            (r"\frac{d$A}{dt} = -$rate $A",), use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] \varnothing }")


class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    @staticmethod
    def rhs(t, A: Reactant, B: Reactant, rate: Parameter):
        delta = rate * A
        return -delta, delta

    def yield_latex_equations(self, *, use_brackets=True):
        yield from self._yield_using_template(
            (r"\frac{d$A}{dt} = -$rate $B", r"\frac{d$B}{dt} = $rate $A"),
            use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] $B }")


class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    @staticmethod
    def rhs(t, A: Reactant, B: Reactant, AB: Reactant, rate: Parameter):
        delta = rate * A * B
        return -delta, -delta, delta

    def yield_latex_equations(self, *, use_brackets=True):
        yield from self._yield_using_template(
            (
                r"\frac{d$A}{dt} = -$rate $A $B",
                r"\frac{d$B}{dt} = -$rate $A $B",
                r"\frac{d$AB}{dt} = $rate $A $B",
            ),
            use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $B ->[$rate] $AB }")


class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    @staticmethod
    def rhs(t, AB: Reactant, A: Reactant, B: Reactant, rate: Parameter):
        delta = rate * AB
        return -delta, delta, delta

    def yield_latex_equations(self, *, use_brackets=True):
        yield from self._yield_using_template(
            (
                r"\frac{d$AB}{dt} = -$rate $AB",
                r"\frac{d$A}{dt} = $rate $AB",
                r"\frac{d$B}{dt} = $rate $AB",
            ),
            use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB ->[$rate] $A + $B }")


class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    @staticmethod
    def rhs(t, A: Reactant, BC: Reactant, AC: Reactant, B: Reactant, rate: Parameter):
        raise NotImplementedError

    def yield_latex_equations(self, use_brackets=True):

        yield from self._yield_using_template(
            (
                r"\frac{d$A}{dt} = -$rate $A $BC",
                r"\frac{d$BC}{dt} = -$rate $A $BC",
                r"\frac{d$AC}{dt} = $rate $A $BC",
                r"\frac{d$B}{dt} = $rate $A $BC",
            ),
            use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $BC ->[$rate] $AC + $B }")


class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    @staticmethod
    def rhs(t, AB: Reactant, CD: Reactant, AD: Reactant, CB: Reactant, rate: Parameter):
        raise NotImplementedError

    def yield_latex_equations(self, use_brackets=True):

        yield from self._yield_using_template(
            (
                r"\frac{d$AB}{dt} = -$rate $AB $CD",
                r"\frac{d$CD}{dt} = -$rate $AB $CD",
                r"\frac{d$AD}{dt} = $rate $AB $CD",
                r"\frac{d$CB}{dt} = $rate $AB $CD",
            ),
            use_brackets=use_brackets,
        )

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB + $CD ->[$rate] $AD + $CB }")
