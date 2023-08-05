from poincare import Variable
from poincare._node import Node
from pytest import mark

from ...core import Compartment, Constant, Parameter, Reaction, Species, initial
from .exporter import SBMLModel
from .importer import convert_model


def equivalent(
    model1: Compartment | type[Compartment], model2: Compartment | type[Compartment]
) -> bool:
    return _equivalent(model1, model2) and _equivalent(model2, model1)


def _equivalent(
    model1: Compartment | type[Compartment], model2: Compartment | type[Compartment]
) -> bool:
    for node1 in model1._yield(Node, exclude=Variable):
        node2 = model2
        for name in str(node1).split("."):
            node2 = getattr(node2, name, None)

        if node1 != node2:
            return False
    else:
        return True


models: list[type[Compartment]] = []


@models.append
class SingleConstant(Compartment):
    k = Constant(default=0)


@models.append
class SingleParameter(Compartment):
    x = Parameter(default=0)


@models.append
class SingleVariable(Compartment):
    x: Species = initial(default=0)


@models.append
class ConstantInConstant(Compartment):
    k = Constant(default=0)
    x = Constant(default=k)


@models.append
class ConstantInParameter(Compartment):
    k = Constant(default=0)
    x = Parameter(default=k)


@models.append
class ConstantInVariable(Compartment):
    k = Constant(default=0)
    x: Species = initial(default=k)


@models.append
class OneReactant(Compartment):
    x: Species = initial(default=0)
    k = Parameter(default=1)
    r = Reaction(reactants=[x], products=(), rate_law=k)


@models.append
class OneProduct(Compartment):
    x: Species = initial(default=0)
    k = Parameter(default=1)
    r = Reaction(reactants=(), products=[x], rate_law=k)


@models.append
class AutoCatalytic(Compartment):
    x: Species = initial(default=0)
    k = Parameter(default=1)
    r = Reaction(reactants=[x], products=[2 * x], rate_law=k)


@mark.parametrize("system", models)
def test_round_trip(system: Compartment):
    sbml = SBMLModel(system)
    model = convert_model(sbml.model)
    assert equivalent(model, system)
