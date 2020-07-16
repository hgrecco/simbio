from simbio.compartments import Compartment, Universe
from simbio.core import Container, Content
from simbio.parameters import Parameter
from simbio.reactants import Reactant
from ward import each, raises, test, xfail

classes = (Content, Container, Reactant, Parameter, Compartment, Universe)


@test("Check protected attributes")
def _():
    protected_attrs = Content._Content__protected_attrs
    assert {"name", "belongs_to"}.issubset(protected_attrs)


@test("Set or del protected attributes in {cls.__name__}")
def _(cls=each(*classes)):
    instance = cls(name="fixed_name", belongs_to=None)

    for attr in Content._Content__protected_attrs:
        with raises(AttributeError):
            setattr(instance, attr, "new_name")

        with raises(AttributeError):
            delattr(isinstance, attr)


@test("{cls.__name__}.name must be valid Python identifier")
def _(cls=each(*classes)):
    for name in ("name.", "1name"):
        with raises(ValueError):
            cls(name=name, belongs_to=None)


@xfail("Not implemented yet")
@test("{cls.__name__}.name must not collide with Simbio methods and attributes")
def _(cls=each(*classes)):
    colliding_name = "name"
    with raises(ValueError):
        cls(name=colliding_name, belongs_to=None)
