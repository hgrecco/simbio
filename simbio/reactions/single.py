"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass

import numpy as np

from ..parameters import Parameter
from ..species import Species
from .core import BaseReaction


class SingleReaction(BaseReaction):
    """Base class for all single reactions."""

    def __init_subclass__(cls):
        """Validates class

        Check if rhs method is well-defined. It must:
        - be a staticmethod
        - have 't' as its first parameter, and the rest must correspond
        to a Species or Parameter class annotation.
        """
        super().__init_subclass__()

        # Check if rhs is a staticmethod
        if not isinstance(inspect.getattr_static(cls, "rhs"), staticmethod):
            raise TypeError(
                f"{cls.__qualname__}.rhs must be a staticmethod. Use @staticmethod decorator."
            )

        # Check rhs signature
        parameters = iter(inspect.signature(cls.rhs).parameters)

        # Check if 't' is the first parameter
        parameter = next(parameters)
        if parameter != "t":
            raise ValueError(
                f"{cls.__qualname__}.rhs first parameter is not t, but {parameter}"
            )

        # Check that all rhs parameter have correct class annotation.
        for parameter in parameters:
            if parameter in cls._species_names:
                continue
            elif parameter in cls._parameter_names:
                continue
            elif parameter in cls.__annotations__:
                raise TypeError(
                    f"{cls.__qualname__}.{parameter} is missing a Species or Parameter class annotation."
                )
            else:
                raise ValueError(
                    f"{cls.__qualname__}.rhs parameter {parameter} is missing from {cls.__qualname__} annotations"
                )

    def _yield_ip_rhs(self, global_species=None, global_parameters=None):
        if global_species is None:
            ix_y = slice(None)
        else:
            local_species = self.species
            ix_y = map(global_species.index, local_species)
            ix_y = np.fromiter(ix_y, dtype=int, count=len(local_species))

        if global_parameters is None:
            ix_p = slice(None)
        else:
            local_parameters = self.parameters
            ix_p = map(global_parameters.index, local_parameters)
            ix_p = np.fromiter(ix_p, dtype=int, count=len(local_parameters))

        def fun(t, y, p, out):
            out[ix_y] += self.rhs(t, *(y[ix_y] ** self.st_numbers), *p[ix_p])

        yield fun

    @staticmethod
    def rhs(t, *args):
        raise NotImplementedError

    def yield_latex_species_values(self, column_separator="&"):
        for name in self._species_names:
            yield getattr(self, name).name
            yield column_separator
            yield getattr(self, name).value

    def yield_latex_parameter_values(self, column_separator="&"):
        for name in self._parameter_names:
            yield getattr(self, name).name
            yield column_separator
            yield getattr(self, name).value


@dataclass
class Creation(SingleReaction):
    """A substance is created from nothing.

      -> A
    """

    A: Species
    rate: Parameter

    @staticmethod
    def rhs(t, A, rate):
        return rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ \varnothing ->[$rate] $A }")


@dataclass
class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A ->
    """

    A: Species
    rate: Parameter

    @staticmethod
    def rhs(t, A, rate):
        return -rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] \varnothing }")


@dataclass
class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    A: Species
    B: Species
    rate: Parameter

    @staticmethod
    def rhs(t, A, B, rate):
        delta = rate * A
        return -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] $B }")


@dataclass
class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    A: Species
    B: Species
    AB: Species
    rate: Parameter

    @staticmethod
    def rhs(t, A, B, AB, rate):
        delta = rate * A * B
        return -delta, -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $B ->[$rate] $AB }")


@dataclass
class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    AB: Species
    A: Species
    B: Species
    rate: Parameter

    @staticmethod
    def rhs(t, AB, A, B, rate):
        delta = rate * AB
        return -delta, delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB ->[$rate] $A + $B }")


@dataclass
class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    A: Species
    BC: Species
    AC: Species
    B: Species
    rate: Parameter

    @staticmethod
    def rhs(t, A, BC, AC, B, rate):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $BC ->[$rate] $AC + $B }")


@dataclass
class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    AB: Species
    CD: Species
    AD: Species
    CB: Species
    rate: Parameter

    @staticmethod
    def rhs(t, AB, CD, AD, CB, rate):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB + $CD ->[$rate] $AD + $CB }")
