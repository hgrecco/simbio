from __future__ import annotations

from simbio import Compartment, Parameter, Species
from simbio.compartments import DuplicateComponentError
from simbio.components import Component
from simbio.reactions import Conversion, Destruction, Synthesis
from ward import each, fixture, raises, test


class Cell(Compartment):
    CO2 = Species(0)
    rate = Parameter(0.5)

    def add_reactions(self):
        yield Conversion(self.Cytoplasm.CO2, self.Nucleus.CO2, self.rate)

    class Cytoplasm(Compartment):
        C = Species(10)
        O2 = Species(10)
        CO2 = Species(0)
        rate = Parameter(1)

        def add_reactions(self):
            yield Synthesis(self.C, self.O2, self.CO2, self.rate)

    class Nucleus(Compartment):
        CO2 = Species(0)
        rate = Parameter(0.1)

        def add_reactions(self):
            yield Destruction(self.CO2, self.rate)


def assert_inherited_contents(BaseModel, Model, overrided: set[str] = None):
    if overrided is None:
        overrided = set()

    for name, component in BaseModel._contents.items():
        new_component = Model[name]

        assert isinstance(new_component, component.__class__)
        assert new_component.name == component.name
        if name not in overrided and isinstance(component, Component):
            assert new_component.value == component.value

        assert new_component.parent is Model


def assert_added_contents(BaseModel, Model, add: dict[str, int] = {}):
    for attr in ("species", "parameters", "compartments", "reactions"):
        assert len(getattr(Model, attr)) == len(getattr(BaseModel, attr)) + add.get(
            attr, 0
        )


@test("Model extension: {instance.__class__.__name__}")
def _(
    instance=each(Species(1), Parameter(1), Compartment()),
    name=each("species", "parameters", "compartments"),
):
    BaseModel = Cell.Cytoplasm

    class Model(BaseModel):
        A = instance

    assert Model is not BaseModel
    assert_inherited_contents(BaseModel, Model)
    assert_added_contents(BaseModel, Model, add={name: 1})


@test("Model extension: Reactions")
def _():
    BaseModel = Cell.Cytoplasm

    class Model(BaseModel):
        def add_reactions(self):
            yield Destruction(self.CO2, self.rate)

    assert Model is not BaseModel
    assert_inherited_contents(BaseModel, Model)
    assert_added_contents(BaseModel, Model, add={"reactions": 1})


@fixture
def simple_model():
    class BaseModel(Compartment):
        A = Species(10)
        B = Species(5)
        rate = Parameter(1)

        class SubModel(Compartment):
            pass

        def add_reactions(self):
            yield Destruction(self.A, self.rate)

    return BaseModel


@test("Inherit after dynamic extension: add_{func}")
def _(BaseModel=simple_model, func=each("species", "parameter", "compartment")):
    getattr(BaseModel, f"add_{func}")("new")

    class Model(BaseModel):
        pass

    assert Model is not BaseModel
    assert_inherited_contents(BaseModel, Model)
    assert_added_contents(BaseModel, Model)


@test("Inherit after dynamic extension: add_reaction")
def _(BaseModel=simple_model):
    BaseModel.add_reaction(Destruction(BaseModel.B, BaseModel.rate))

    class Model(BaseModel):
        pass

    assert Model is not BaseModel
    assert_inherited_contents(BaseModel, Model)
    assert_added_contents(BaseModel, Model)


@test("Override Species: {BaseModel.name}")
def _(BaseModel=each(Cell, Cell.Cytoplasm, Cell.Nucleus)):
    with raises(DuplicateComponentError):

        class WrongModel(BaseModel):
            CO2 = Species(20)

    class Model(BaseModel):
        CO2 = Species(20, override=True)

    assert_inherited_contents(BaseModel, Model, overrided={"CO2"})
    assert_added_contents(BaseModel, Model)


@test("Override Parameter: {BaseModel.name}")
def _(BaseModel=each(Cell, Cell.Cytoplasm, Cell.Nucleus)):
    with raises(DuplicateComponentError):

        class WrongModel(BaseModel):
            rate = Parameter(2)

    class Model(BaseModel):
        rate = Parameter(2, override=True)

    assert_inherited_contents(BaseModel, Model, overrided={"rate"})
    assert_added_contents(BaseModel, Model)


@test("Override Compartment")
def _():
    with raises(DuplicateComponentError):

        class WrongNewCell(Cell):
            class Cytoplasm(Compartment):
                pass

    class NewCell(Cell):
        class Cytoplasm(Cell.Cytoplasm):
            pass

    assert_inherited_contents(Cell, NewCell)
    assert_added_contents(Cell, NewCell)


@test("Override Reaction")
def _():
    BaseModel = Cell.Cytoplasm

    with raises(DuplicateComponentError):

        class WrongModel(BaseModel):
            new_rate = Parameter(2)

            def add_reactions(self):
                yield Synthesis(self.C, self.O2, self.CO2, self.new_rate)

    class Model(BaseModel):
        new_rate = Parameter(2)

        def override_reactions(self):
            yield Synthesis(self.C, self.O2, self.CO2, self.new_rate)

    assert_inherited_contents(BaseModel, Model)
    assert_added_contents(BaseModel, Model, {"parameters": 1})


@test("Don't override with different type")
def _():
    with raises(TypeError):

        class SpeciesToParameter(Cell.Cytoplasm):
            C = Parameter(0, override=True)

    with raises(TypeError):

        class SpeciesToCompartment(Cell.Cytoplasm):
            class C(Compartment):
                pass

    with raises(TypeError):

        class ParameterToSpecies(Cell.Cytoplasm):
            rate = Species(0, override=True)

    with raises(TypeError):

        class ParameterToCompartment(Cell.Cytoplasm):
            class rate(Compartment):
                pass

    with raises(TypeError):

        class CompartmentToSpecies(Cell):
            Cytoplasm = Species(0, override=True)

    with raises(TypeError):

        class CompartmentToParameter(Cell):
            Cytoplasm = Parameter(0, override=True)
