from typing import Callable

import libsbml
from poincare import Parameter, Variable
from poincare.types import Node, System

from ...core import Constant, Reaction
from .mathML import mathMLExporter


@mathMLExporter.to_mathML.register
def _(self: mathMLExporter, x: Node):
    node = libsbml.ASTNode(libsbml.AST_NAME)
    node.setId(self.identity(x))
    node.setName(self.namer(x.name))
    return node


def raise_on_error(error: int):
    if error != 0:
        message = libsbml.OperationReturnValue_toString(error)
        raise RuntimeError(message)


def default_name(x: str):
    return x


def default_id(x: Node):
    return str(x).removeprefix(".")


class SBMLModel:
    def __init__(
        self,
        model: System | type[System],
        *,
        level: tuple[int, int] = (3, 2),
        identity_mapper: Callable[[Node], str] = default_id,
        name_mapper: Callable[[str], str] = default_name,
    ):
        self.level = level
        self.identity_mapper = identity_mapper
        self.name_mapper = name_mapper
        self.to_mathML = mathMLExporter(
            namer=name_mapper,
            identity=identity_mapper,
        ).to_mathML

        self.model = libsbml.Model(*self.level)
        self.model.setName(self.name_mapper(model.name))
        for c in model._yield(Constant):
            self.add_parameter(c, constant=True)
        for p in model._yield(Parameter, exclude=Variable):
            self.add_parameter(p, constant=False)
        for s in model._yield(Variable):
            self.add_species(s)
        for r in model._yield(Reaction):
            self.add_reaction(r)

    def add_parameter(self, p: Parameter | Constant, *, constant: bool):
        parameter: libsbml.Parameter = self.model.createParameter()
        raise_on_error(parameter.setId(self.identity_mapper(p)))
        raise_on_error(parameter.setName(self.name_mapper(p.name)))
        raise_on_error(parameter.setConstant(constant))
        if isinstance(p.default, Constant):
            assignment: libsbml.InitialAssignment = self.model.createInitialAssignment()
            raise_on_error(assignment.setMath(self.to_mathML(p.default)))
            raise_on_error(assignment.setSymbol(parameter.getId()))
        else:
            raise_on_error(parameter.setValue(p.default))

    def add_species(self, s: Variable):
        species: libsbml.Species = self.model.createSpecies()
        raise_on_error(species.setId(self.identity_mapper(s)))
        raise_on_error(species.setName(self.name_mapper(s.name)))
        if isinstance(s.initial, Constant):
            assignment: libsbml.InitialAssignment = self.model.createInitialAssignment()
            raise_on_error(assignment.setMath(self.to_mathML(s.initial)))
            raise_on_error(assignment.setSymbol(species.getId()))
        else:
            raise_on_error(species.setInitialAmount(s.initial))

    def add_reaction(self, r: Reaction, *, reversible: bool = False):
        reaction: libsbml.Reaction = self.model.createReaction()
        reaction.setId(self.identity_mapper(r))
        reaction.setName(r.name)
        for s in r.reactants:
            sr: libsbml.SpeciesReference = self.model.createReactant()
            sr.setSpecies(self.identity_mapper(s.variable))
            sr.setStoichiometry(s.stoichiometry)
        for s in r.products:
            sr: libsbml.SpeciesReference = self.model.createProduct()
            sr.setSpecies(self.identity_mapper(s.variable))
            sr.setStoichiometry(s.stoichiometry)
        reaction.setReversible(reversible)
        kinetic_law: libsbml.KineticLaw = self.model.createKineticLaw()
        kinetic_law.setMath(self.to_mathML(r.rate_law))

    def to_sbml(self) -> str:
        return self.model.toSBML()
