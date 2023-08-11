import math
from collections import ChainMap
from typing import Callable, TypeVar

import libsbml
from symbolite import Symbol
from symbolite import abstract as libabstract
from symbolite.core import as_function

from ...core import Compartment, Constant, Parameter, Reaction, Species, initial
from .mathML.importer import from_mathML, mapper

T = TypeVar("T")


class DynamicCompartment:
    def __init__(self, name: str):
        self.compartment = type(name, (Compartment,), {})

    def add(self, name: str, value):
        value.__set_name__(self.compartment, name)
        setattr(self.compartment, name, value)

    def __getattr__(self, name):
        try:
            return getattr(self.compartment, name)
        except AttributeError as e:
            e.add_note("component not found in Compartment")
            raise


def read_model(
    file: str,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    with open(file) as f:
        text = f.read()
    return parse_model(text, name=name, identity_mapper=identity_mapper)


def parse_model(
    sbml: str,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    document: libsbml.SBMLDocument = libsbml.readSBMLFromString(sbml)
    if document.getNumErrors() != 0:
        raise RuntimeError("error reading the SBML file")

    model: libsbml.Model = document.getModel()
    return convert_model(model, name=name, identity_mapper=identity_mapper)


def convert_model(
    model: libsbml.Model,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
) -> type[Compartment]:
    return SBMLImporter(
        model, name=name, identity_mapper=identity_mapper
    ).simbio.compartment


class SBMLImporter:
    def __init__(
        self,
        model: libsbml.Model,
        *,
        name: str | None = None,
        identity_mapper: Callable[[str], str] = lambda x: x,
    ):
        if name is None:
            name: str = model.getName()
        self.model = model
        self.simbio = DynamicCompartment(name)
        self.identity = identity_mapper
        self.mapper = ChainMap({}, mapper)

        self.functions = {}
        self.mapper[libsbml.AST_FUNCTION] = self.functions
        for f in model.getListOfFunctionDefinitions():
            f: libsbml.FunctionDefinition
            self.functions[f.getId()] = self.create_function(f)

        for p in model.getListOfParameters():
            self.add_parameter(p)

        for s in model.getListOfSpecies():
            self.add_species(s)

        for r in model.getListOfReactions():
            self.add_reaction(r)

    def add_parameter(self, p: libsbml.Parameter):
        name = self.identity(p.getId())
        if not math.isnan(value := p.getValue()):
            pass
        else:
            value = self.get_assignment(p)
        if p.getConstant():
            self.simbio.add(name, Constant(default=value))
        else:
            self.simbio.add(name, Parameter(default=value))

    def get_assignment(self, node: libsbml.ASTNode):
        assign: libsbml.InitialAssignment = self.model.getInitialAssignment(
            node.getId()
        )
        math_ast: libsbml.ASTNode = assign.getMath()
        value = self.formula_to_symbolite(math_ast)
        return value

    def add_species(self, s: libsbml.Species):
        name = self.identity(s.getId())
        if not math.isnan(value := s.getInitialConcentration()):
            pass
        elif not math.isnan(value := s.getInitialAmount()):
            pass
        else:
            value = self.get_assignment(s)

        self.simbio.add(name, initial(default=value))

    def get_symbol(self, name: str, expected_type: type[T] = object) -> T:
        value = getattr(self.simbio, name)
        if not isinstance(value, expected_type):
            raise TypeError(f"unexpected type: {type(value)}")
        return value

    def get_species_reference(self, s: libsbml.SpeciesReference) -> Species:
        name = self.identity(s.getSpecies())
        species = self.get_symbol(name, Species)
        st = s.getStoichiometry()
        if math.isnan(st):
            st = 1
        return st * species

    def formula_to_symbolite(self, ast_node: libsbml.ASTNode):
        symbolite_node: Symbol = from_mathML(ast_node, self.mapper)
        names = symbolite_node.symbol_names()
        mapper = {}
        for n in names:
            s = self.get_symbol(self.identity(n))
            if isinstance(s, Species):
                s = s.variable
            mapper[n] = s
        formula = symbolite_node.subs_by_name(**mapper)
        return formula

    def _add_reaction(
        self,
        name: str,
        reactants: list[Species],
        products: list[Species],
        formula: libsbml.ASTNode,
    ):
        self.simbio.add(
            name,
            Reaction(
                reactants=reactants,
                products=products,
                rate_law=self.formula_to_symbolite(formula),
            ),
        )

    def add_reaction(self, r: libsbml.Reaction):
        reactants = [self.get_species_reference(s) for s in r.getListOfReactants()]
        products = [self.get_species_reference(s) for s in r.getListOfProducts()]
        kinetic_law: libsbml.KineticLaw = r.getKineticLaw()
        formula: libsbml.ASTNode = kinetic_law.getMath()
        name = r.getName()
        if r.getReversible():
            if formula.getType() != libsbml.AST_MINUS:
                raise ValueError(
                    "reversible formula without minus", kinetic_law.getFormula()
                )
            forward: libsbml.ASTNode = formula.getLeftChild()
            reverse: libsbml.ASTNode = formula.getRightChild()
            self._add_reaction(f"{name}_forward", reactants, products, forward)
            self._add_reaction(f"{name}_reverse", products, reactants, reverse)
        else:
            self._add_reaction(name, reactants, products, formula)

    def create_function(self, func: libsbml.FunctionDefinition):
        f: libsbml.ASTNode = func.getMath()
        children: list[Symbol] = [
            from_mathML(f.getChild(i), mapper=self.mapper)
            for i in range(f.getNumChildren())
        ]
        params = children[:-1]
        body = children[-1]
        return as_function(
            body,
            func.getId(),
            tuple(map(str, params)),
            libsl=libabstract,
        )
