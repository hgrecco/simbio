from string import Template
from typing import Callable, Generator, Tuple

import numpy as np

from ..parameters import Parameter
from ..reactants import Reactant

try:
    from sympy import symbols, Derivative, Equality
except ImportError:

    def symbols(*args, **kwargs):
        raise Exception(
            "This function requires sympy. Please install it:\n"
            "\tpip install sympy\n"
            "\t\t\tor\n"
            "\tconda install sympy\n"
        )

    Derivative = Equality = symbols

ODE_Fun = Callable[[float, np.ndarray, np.ndarray], None]


class BaseReaction:
    """Base class of all single and compound reactions.

    The constructor automatically assign the kwargs to the attribute value.
    """

    _reactant_names: Tuple[str, ...] = ()
    _parameter_names: Tuple[str, ...] = ()
    st_numbers: np.ndarray

    @property
    def reactants(self) -> Tuple[Reactant, ...]:
        """Return a tuple of the reactants in this reaction."""
        return tuple(getattr(self, name) for name in self._reactant_names)

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        """Return a tuple of the parameters in this reaction."""
        return tuple(getattr(self, name) for name in self._parameter_names)

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

    # Latex
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
        t = symbols("t")
        reactants = self.reactants
        if use_brackets:
            reactants = (f"[{x}]" for x in reactants)
        reactants = tuple(map(symbols, reactants))
        parameters = map(symbols, self.parameters)

        for lhs, rhs in zip(reactants, self.rhs(t, *reactants, *parameters)):
            yield Equality(Derivative(lhs, t), rhs)

    def yield_latex_reaction(self):
        # Use \usepackage{mhchem}
        raise NotImplementedError

    def yield_latex_reactant_values(self):
        raise NotImplementedError

    def yield_latex_parameter_values(self):
        raise NotImplementedError
