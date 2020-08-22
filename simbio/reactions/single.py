"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects species to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import inspect
from typing import get_type_hints

import numpy as np

from ..parameters import Parameter
from ..species import Species
from .core import BaseReaction, _check_signature


class SingleReaction(BaseReaction):
    """Base class for all single reactions."""

    def __init_subclass__(cls):
        """Initialize class from rhs method.

        Check if rhs method is well-defined. It must:
        - be a staticmethod
        - have an ordered signature (t, *Species, *Parameters)

        Continue class initialization with rhs annotations in BaseReaction.
        """

        # Check if staticmethod
        if not isinstance(inspect.getattr_static(cls, "rhs"), staticmethod):
            raise TypeError(
                f"{cls.__name__}.rhs must be a staticmethod. Use @staticmethod decorator."
            )

        # Evaluate annotations
        rhs_annotations = cls.rhs.__annotations__ = get_type_hints(cls.rhs)

        # Check signature order
        _check_signature(cls.rhs, t_first=True)

        # Set class annotations from rhs
        if "t" in rhs_annotations:
            rhs_annotations.pop("t")

        return super().__init_subclass__(annotations=rhs_annotations)

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


class Creation(SingleReaction):
    """A substance is created from nothing.

      -> A
    """

    @staticmethod
    def rhs(t, A: Species, rate: Parameter):
        return rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ \varnothing ->[$rate] $A }")


class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A ->
    """

    @staticmethod
    def rhs(t, A: Species, rate: Parameter):
        return -rate * A

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] \varnothing }")


class Conversion(SingleReaction):
    """A substance convert to another.

    A -> B
    """

    @staticmethod
    def rhs(t, A: Species, B: Species, rate: Parameter):
        delta = rate * A
        return -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A ->[$rate] $B }")


class Synthesis(SingleReaction):
    """Two or more simple substances combine to form a more complex substance.

    A + B -> AB
    """

    @staticmethod
    def rhs(t, A: Species, B: Species, AB: Species, rate: Parameter):
        delta = rate * A * B
        return -delta, -delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $B ->[$rate] $AB }")


class Dissociation(SingleReaction):
    """A more complex substance breaks down into its more simple parts.

    AB -> A + B
    """

    @staticmethod
    def rhs(t, AB: Species, A: Species, B: Species, rate: Parameter):
        delta = rate * AB
        return -delta, delta, delta

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB ->[$rate] $A + $B }")


class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    @staticmethod
    def rhs(t, A: Species, BC: Species, AC: Species, B: Species, rate: Parameter):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $BC ->[$rate] $AC + $B }")


class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    @staticmethod
    def rhs(t, AB: Species, CD: Species, AD: Species, CB: Species, rate: Parameter):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB + $CD ->[$rate] $AD + $CB }")
