"""
    simbio.reactions
    ~~~~~~~~~~~~~~~~

    A reaction connects reactants to their rate of change.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import inspect

import numpy as np

from ..parameters import Parameter
from ..reactants import Reactant
from .core import BaseReaction, _check_signature


class SingleReaction(BaseReaction):
    """Base class for all single reactions."""

    def __init_subclass__(cls):
        """Initialize class from rhs method.

        Check if rhs method is well-defined. It must:
        - be a staticmethod
        - have an ordered signature (t, *Reactants, *Parameters)

        Continue class initialization with rhs annotations in BaseReaction.
        """

        # Check if staticmethod
        if not isinstance(inspect.getattr_static(cls, "rhs"), staticmethod):
            raise TypeError(
                f"{cls.__name__}.rhs must be a staticmethod. Use @staticmethod decorator."
            )

        # Check signature order
        _check_signature(cls.rhs, t_first=True)

        # Set class annotations from rhs
        rhs_annotations = cls.rhs.__annotations__
        if "t" in rhs_annotations:
            rhs_annotations.pop("t")

        return super().__init_subclass__(annotations=rhs_annotations)

    def yield_ip_rhs(self, global_reactants=None, global_parameters=None):
        if global_reactants is None:
            ix = slice(None)
        else:
            local_reactants = self.reactants
            ix = map(global_reactants.index, local_reactants)
            ix = np.fromiter(ix, dtype=int, count=len(local_reactants))

        parameters = {
            name: global_parameters.get(p, p.value)
            for name, p in zip(self._parameter_names, self.parameters)
        }

        def fun(t, y, out):
            out[ix] += self.rhs(t, *(y[ix] ** self.st_numbers), **parameters)

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

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ \varnothing ->[$rate] $A }")


class Destruction(SingleReaction):
    """A substance degrades into nothing.

    A ->
    """

    @staticmethod
    def rhs(t, A: Reactant, rate: Parameter):
        return -rate * A

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

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB ->[$rate] $A + $B }")


class SingleReplacement(SingleReaction):
    """A single uncombined element replaces another in a compound.

    A + BC -> AC + B
    """

    @staticmethod
    def rhs(t, A: Reactant, BC: Reactant, AC: Reactant, B: Reactant, rate: Parameter):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $A + $BC ->[$rate] $AC + $B }")


class DoubleReplacement(SingleReaction):
    """The anions and cations of two compounds switch places and form two entirely different compounds.

    AB + CD -> AD + CB
    """

    @staticmethod
    def rhs(t, AB: Reactant, CD: Reactant, AD: Reactant, CB: Reactant, rate: Parameter):
        raise NotImplementedError

    def yield_latex_reaction(self):
        yield self._template_replace(r"\ce{ $AB + $CD ->[$rate] $AD + $CB }")
