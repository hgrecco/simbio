import numpy as np
from simbio.compartments import Universe
from simbio.reactions import Conversion, Creation
from ward import fixture, raises, test


@fixture
def data():
    cell = Universe(name="cell")
    reactant = cell.add_species("reactant", 1)
    parameter = cell.add_parameter("parameter", 2)

    nucleus = cell.add_compartment("nucleus")
    nucleus_reactant = nucleus.add_species("reactant", 3)
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


@test("Retrieve species, parameters, and compartments")
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


@test("Return all Compartment species")
def _(d=data):
    cell = d["cell"]
    assert cell.species == (d["reactant"], d["nucleus.reactant"])

    nucleus = d["nucleus"]
    assert nucleus.species == (d["nucleus.reactant"],)


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

    # Species does not belong
    with raises(Exception):
        nucleus.add_reaction(Creation(cell.reactant, nucleus.parameter))

    # Parameter does not belong
    with raises(Exception):
        nucleus.add_reaction(Creation(nucleus.reactant, cell.parameter))


@test("Build Compartment concentration and parameter vectors")
def _(data=data):
    cell, nucleus = data["cell"], data["nucleus"]

    # Cell
    y0, p = cell._build_value_vectors()
    assert np.allclose(y0, np.array([1.0, 3.0]))
    assert np.allclose(p, np.array([2.0, 4.0]))

    # Nucleus
    y0, p = nucleus._build_value_vectors()
    assert np.allclose(y0, np.array([3.0]))
    assert np.allclose(p, np.array([4.0]))

    # Override defaults in cell
    y0, p = cell._build_value_vectors(
        {
            cell.reactant: 2.0,
            "parameter": 3.0,
            "nucleus.reactant": 4.0,
            nucleus.parameter: 5.0,
        }
    )
    assert np.allclose(y0, np.array([2.0, 4.0]))
    assert np.allclose(p, np.array([3.0, 5.0]))

    # Non-existing
    with raises(ValueError):
        cell._build_value_vectors({"non_existing": 3})
    cell._build_value_vectors({"non_existing": 3}, raise_on_unexpected=False)

    # Outside compartment
    values = {cell.reactant: 3, cell.parameter: 3}
    with raises(ValueError):
        nucleus._build_value_vectors(values)
    nucleus._build_value_vectors(values, raise_on_unexpected=False)
