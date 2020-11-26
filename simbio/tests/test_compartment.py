import numpy as np
from simbio.compartments import Compartment
from simbio.reactions import Conversion, Creation, Destruction, Synthesis
from ward import fixture, raises, test, xfail


@fixture
def data():
    cell = Compartment(name="cell")
    reactant = cell.add_species("reactant", 1)
    parameter = cell.add_parameter("parameter", 2)

    nucleus = cell.add_compartment("nucleus")
    nucleus_reactant = nucleus.add_species("reactant", 3)
    nucleus_parameter = nucleus.add_parameter("parameter", 4)

    reaction1 = Creation(cell.reactant, cell.parameter)
    cell.add_reaction(reaction1)
    reaction2 = Creation(nucleus.reactant, nucleus.parameter)
    nucleus.add_reaction(reaction2)
    reaction3 = Conversion(cell.reactant, nucleus.reactant, nucleus.parameter)
    cell.add_reaction(reaction3)

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

    nucleus.add_reaction(Destruction(A=nucleus.reactant, rate=nucleus.parameter))

    # Species does not belong
    with raises(Exception):
        nucleus.add_reaction(Destruction(A=cell.reactant, rate=nucleus.parameter))

    # Parameter does not belong
    with raises(Exception):
        nucleus.add_reaction(Destruction(A=nucleus.reactant, rate=cell.parameter))


@test("Add reaction at wrong level")
def _(d=data):
    """Since a reaction can only be added at a unique compartment,
    the first common parent of its species and parameters,
    it prevents adding the reaction more than once at different levels.
    """
    cell = d["cell"]

    nucleolus = cell.nucleus.add_compartment("nucleolus")
    nucleolus.add_species("reactant", 5)
    nucleolus.add_parameter("parameter", 6)

    reaction = Creation(A=nucleolus.reactant, rate=nucleolus.parameter)
    with raises(Exception):
        cell.add_reaction(reaction)
    with raises(Exception):
        cell.nucleus.add_reaction(reaction)
    cell.nucleus.nucleolus.add_reaction(reaction)

    reaction = Conversion(
        A=nucleolus.reactant, B=cell.nucleus.reactant, rate=cell.nucleus.parameter
    )
    with raises(Exception):
        cell.add_reaction(reaction)
    with raises(Exception):
        cell.nucleus.nucleolus.add_reaction(reaction)
    cell.nucleus.add_reaction(reaction)


@test("Add duplicate reaction")
def _():
    cell = Compartment(name="cell")
    A = cell.add_species("A")
    B = cell.add_species("B")
    C = cell.add_species("C")

    k1 = cell.add_parameter("k1")
    k2 = cell.add_parameter("k2")

    cell.add_reaction(Synthesis(A=A, B=B, AB=C, rate=k1))

    # Identical reactions
    with raises(Exception):
        cell.add_reaction(Synthesis(A=A, B=B, AB=C, rate=k1))

    # Identical reaction switching A and B
    with raises(Exception):
        cell.add_reaction(Synthesis(A=B, B=A, AB=C, rate=k1))

    # Equivalent reaction with different paramenter
    with raises(Exception):
        cell.add_reaction(Synthesis(A=A, B=B, AB=C, rate=k2))

    cell.add_reaction(Synthesis(A=A, B=B, AB=C, rate=k1), override=True)
    cell.add_reaction(Synthesis(A=A, B=C, AB=B, rate=k1))  # It's a different reaction


@xfail("Functionality moved to Builder class")
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
