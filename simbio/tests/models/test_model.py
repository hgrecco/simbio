from simbio import Compartment, Parameter, Species
from simbio.reactions import Conversion, Synthesis
from ward import each, test


class SingleCompartment(Compartment):
    C = Species(10)
    O2 = Species(10)
    CO2 = Species(0)
    rate = Parameter(1)

    def add_reactions(self):
        yield Synthesis(self.C, self.O2, self.CO2, self.rate)


class NestedModel(Compartment):
    rate = Parameter(0.1)

    class InnerCompartment(Compartment):
        C = Species(10)
        O2 = Species(10)
        CO2 = Species(0)
        rate = Parameter(1)

        def add_reactions(self):
            yield Synthesis(self.C, self.O2, self.CO2, self.rate)

    class InnerCompartment2(Compartment):
        CO2 = Species(0)

    def add_reactions(self):
        yield Conversion(
            self.InnerCompartment.CO2, self.InnerCompartment2.CO2, self.rate
        )


@test("Species")
def _(Model=SingleCompartment):
    assert len(Model.species) == 3
    assert isinstance(Model.C, Species)
    assert Model.C.name == "C"
    assert Model.C.parent is Model
    assert Model.C.value == 10


@test("Parameters")
def _(Model=each(SingleCompartment, NestedModel.InnerCompartment)):
    assert len(Model.parameters) == 1
    assert isinstance(Model.rate, Parameter)
    assert Model.rate.name == "rate"
    assert Model.rate.parent is Model
    assert Model.rate.value == 1


@test("Compartments")
def _(Model=each(SingleCompartment, NestedModel.InnerCompartment)):
    assert len(Model.compartments) == 0


@test("Reactions")
def _(Model=each(SingleCompartment, NestedModel.InnerCompartment)):
    assert len(Model.reactions) == 1
    assert isinstance(Model.reactions[0], Synthesis)


#
# Nested model
#
@test("Nested model: Species")
def _():
    assert len(NestedModel.species) == 4
    assert len(NestedModel.InnerCompartment.species) == 3
    assert len(NestedModel.InnerCompartment2.species) == 1

    for name in ("InnerCompartment", "InnerCompartment2"):
        assert isinstance(NestedModel[name].CO2, Species)
        assert NestedModel[name].CO2.name == "CO2"
        assert NestedModel[name].CO2.parent is NestedModel[name]
        assert NestedModel[name].CO2.value == 0


@test("Nested model: Parameters")
def _():
    assert len(NestedModel.parameters) == 2
    assert len(NestedModel.InnerCompartment.parameters) == 1
    assert len(NestedModel.InnerCompartment2.parameters) == 0

    assert isinstance(NestedModel.rate, Parameter)
    assert NestedModel.rate.name == "rate"
    assert NestedModel.rate.parent is NestedModel
    assert NestedModel.rate.value == 0.1

    assert isinstance(NestedModel.InnerCompartment.rate, Parameter)
    assert NestedModel.InnerCompartment.rate.name == "rate"
    assert NestedModel.InnerCompartment.rate.parent is NestedModel.InnerCompartment
    assert NestedModel.InnerCompartment.rate.value == 1


@test("Nested model: Compartments")
def _():
    assert len(NestedModel.compartments) == 2

    for name in ("InnerCompartment", "InnerCompartment2"):
        assert len(NestedModel[name].compartments) == 0
        assert issubclass(NestedModel[name], Compartment)
        assert NestedModel[name].name == name
        assert NestedModel[name].parent is NestedModel


@test("Nested model: Reactions")
def _():
    assert len(NestedModel.reactions) == 2
    assert len(NestedModel.InnerCompartment.reactions) == 1
    assert len(NestedModel.InnerCompartment2.reactions) == 0
