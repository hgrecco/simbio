import numpy as np
from simbio.compartments import Universe
from simbio.reactions import Conversion, Creation
from ward import fixture, raises, test


@fixture
def data():
    cell = Universe(name="cell")
    reactant = cell.add_reactant("reactant", 1)
    parameter = cell.add_parameter("parameter", 2)

    nucleus = cell.add_compartment("nucleus")
    nucleus_reactant = nucleus.add_reactant("reactant", 3)
    nucleus_parameter = nucleus.add_parameter("parameter", 4)

    reaction1 = cell.add_reaction(Creation(cell.reactant, cell.parameter))
    reaction2 = nucleus.add_reaction(Creation(nucleus.reactant, nucleus.parameter))
    reaction3 = cell.add_reaction(
        Conversion(cell.reactant, nucleus.reactant, nucleus.parameter)
    )

    return {
        "cell": cell,
        "reactant": reactant,
        "parameter": parameter,
        "nucleus": nucleus,
        "nucleus.reactant": nucleus_reactant,
        "nucleus.parameter": nucleus_parameter,
        "reaction1": reaction1,
        "reaction2": reaction2,
        "reaction3": reaction3,
    }


@test("Retrieve reactants, parameters, and compartments")
def _(data=data):
    cell = data.pop("cell")

    for key, value in data.items():
        if "reaction" in key:
            continue
        assert getattr(cell, key) is value
        assert cell[key] is value


@test("Return all Compartment parameters")
def _(d=data):
    cell = d["cell"]
    assert cell.parameters == (d["parameter"], d["nucleus.parameter"])

    nucleus = d["nucleus"]
    assert nucleus.parameters == (d["nucleus.parameter"],)


@test("Return all Compartment reactants")
def _(d=data):
    cell = d["cell"]
    assert cell.reactants == (d["reactant"], d["nucleus.reactant"])

    nucleus = d["nucleus"]
    assert nucleus.reactants == (d["nucleus.reactant"],)


@test("Return all Compartment compartments")
def _(d=data):
    cell = d["cell"]
    assert cell.compartments == (d["nucleus"],)

    nucleus = d["nucleus"]
    assert nucleus.compartments == ()


@test("Return all Compartment reactions")
def _(d=data):
    cell = d["cell"]
    assert cell.reactions == (d["reaction1"], d["reaction3"], d["reaction2"])

    nucleus = d["nucleus"]
    assert nucleus.reactions == (d["reaction2"],)


@test("Add reaction with non-compartment components")
def _(d=data):
    cell = d["cell"]
    nucleus = cell.nucleus

    nucleus.add_reaction(Creation(nucleus.reactant, nucleus.parameter))

    # Reactant does not belong
    with raises(Exception):
        nucleus.add_reaction(Creation(cell.reactant, nucleus.parameter))

    # Parameter does not belong
    with raises(Exception):
        nucleus.add_reaction(Creation(nucleus.reactant, cell.parameter))


@test("Build Compartment concentration vector")
def _(data=data):
    cell = data["cell"]
    assert np.allclose(cell._build_concentration_vector(), np.array([1.0, 3.0]))

    nucleus = data["nucleus"]
    assert np.allclose(nucleus._build_concentration_vector(), np.array([3.0]))

    assert np.allclose(
        cell._build_concentration_vector({cell.reactant: 2.0}), np.array([2.0, 3.0])
    )
    assert np.allclose(
        cell._build_concentration_vector({"nucleus.reactant": 5.0}),
        np.array([1.0, 5.0]),
    )
    assert np.allclose(
        nucleus._build_concentration_vector({nucleus.reactant: 4.0}), np.array([4.0])
    )

    with raises(KeyError):
        cell._build_concentration_vector({"non_existing_reactant": 3})

    with raises(ValueError):
        # Outside compartment
        nucleus._build_concentration_vector({cell.reactant: 3})

    with raises(ValueError):
        # Not a reactant
        nucleus._build_concentration_vector({nucleus.parameter: 3})


@test("Build Compartment parameter vector")
def _(data=data):
    cell = data["cell"]
    assert np.allclose(cell._build_parameter_vector(), np.array([2.0, 4.0]))

    nucleus = data["nucleus"]
    assert np.allclose(nucleus._build_parameter_vector(), np.array([4.0]))

    assert np.allclose(
        cell._build_parameter_vector({cell.parameter: 3.0}), np.array([3.0, 4.0])
    )
    assert np.allclose(
        cell._build_parameter_vector({"nucleus.parameter": 5.0}), np.array([2.0, 5.0]),
    )
    assert np.allclose(
        nucleus._build_parameter_vector({nucleus.parameter: 5.0}), np.array([5.0])
    )

    with raises(KeyError):
        cell._build_parameter_vector({"non_existing_parameter": 3})

    with raises(ValueError):
        # Outside compartment
        nucleus._build_parameter_vector({cell.parameter: 3})

    with raises(ValueError):
        # Not a parameter
        nucleus._build_parameter_vector({nucleus.reactant: 3})
