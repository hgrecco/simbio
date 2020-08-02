from dataclasses import FrozenInstanceError

from simbio.compartments import Compartment, Universe
from simbio.core import Container, Content
from simbio.parameters import Parameter
from simbio.reactants import Reactant
from ward import each, raises, test, xfail

classes = (Content, Container, Reactant, Parameter, Compartment, Universe)


@test("Set or del protected attributes in {cls.__name__}")
def _(cls=each(*classes)):
    instance = cls(name="fixed_name", belongs_to=None)

    for attr in Content.__annotations__:
        with raises(FrozenInstanceError):
            setattr(instance, attr, "new_name")

        with raises(FrozenInstanceError):
            delattr(instance, attr)


@test("Hash and equality by id in {cls.__name__}")
def _(cls=each(*classes)):
    obj1 = cls(name="name", belongs_to=None)
    obj2 = cls(name="name", belongs_to=None)

    assert hash(obj1) == id(obj1)
    assert obj1 == obj1
    assert obj1 != obj2


@test("Copy {cls.__name__}")
def _(cls=each(*classes)):
    base_obj = cls(name="name", belongs_to=None)

    new_name = base_obj.copy(name="new_name")
    assert new_name.name == "new_name"
    assert new_name.belongs_to is None

    new_belong = base_obj.copy(belongs_to="container")
    assert new_belong.name == base_obj.name
    assert new_belong.belongs_to == "container"


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
