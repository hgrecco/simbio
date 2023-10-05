import math

from pytest import mark, raises

from ...core import Parameter, Species
from . import types
from .importer import convert, nan_to_none


@mark.parametrize("value", [None, math.nan, 1.0])
@mark.parametrize("units", [None])
@mark.parametrize("constant", [False, True])
def test_parameter(value, units, constant):
    name = types.ID("p")
    model = types.Model(
        parameters=[
            types.Parameter(
                id=name,
                value=value,
                units=units,
                constant=constant,
            )
        ],
    )

    compartment = convert(model, name="model")
    p = getattr(compartment, name)
    assert isinstance(p, Parameter)
    assert p.default == nan_to_none(value)


@mark.parametrize("initial_amount", [None, math.nan, 0, 1])
@mark.parametrize("initial_concentration", [None, math.nan, 0, 1])
@mark.parametrize("substance_units", [None])
@mark.parametrize("has_only_substance_units", [False, True])
@mark.parametrize("boundary_condition", [False, True])
@mark.parametrize("constant", [False, True])
@mark.parametrize("conversion_factor", [None])
def test_species(
    initial_amount,
    initial_concentration,
    substance_units,
    has_only_substance_units,
    boundary_condition,
    constant,
    conversion_factor,
):
    name = types.ID("s")
    compartment = types.ID("c")
    model = types.Model(
        species=[
            types.Species(
                id=name,
                compartment=compartment,
                initial_amount=initial_amount,
                initial_concentration=initial_concentration,
                substance_units=substance_units,
                has_only_substance_units=has_only_substance_units,
                boundary_condition=boundary_condition,
                constant=constant,
                conversion_factor=conversion_factor,
            )
        ],
    )

    initial_amount = nan_to_none(initial_amount)
    initial_concentration = nan_to_none(initial_concentration)
    if initial_amount is not None and initial_concentration is not None:
        with raises(ValueError):
            convert(model, name="model")
    else:
        compartment = convert(model, name="model")
        s = getattr(compartment, name)
        assert isinstance(s, Species)
        if initial_amount is None:
            assert s.variable.initial == initial_concentration
        else:
            assert s.variable.initial == initial_amount


@mark.parametrize("spatial_dimensions", [None, 3])
@mark.parametrize("size", [None, math.nan, 1])
@mark.parametrize("units", [None])
@mark.parametrize("constant", [False, True])
def test_compartment(spatial_dimensions, size, units, constant):
    name = types.ID("c")
    model = types.Model(
        compartments=[
            types.Compartment(
                id=name,
                spatial_dimensions=spatial_dimensions,
                size=size,
                units=units,
                constant=constant,
            )
        ],
    )

    compartment = convert(model, name="model")
    p = getattr(compartment, name)
    assert isinstance(p, Parameter)
    assert p.default == nan_to_none(size)
