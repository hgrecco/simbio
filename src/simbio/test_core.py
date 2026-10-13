import numpy as np
from poincare import Independent, System, Variable

from . import (
    AbsoluteRateLaw,
    Compartment,
    MassAction,
    Parameter,
    RateLaw,
    Simulator,
    Species,
    assign,
    Reactant,
    reaction_initial,
)
from .core import (
    Volume,
    amount,
    compensate_volume,
    concentration,
    make_concentration,
    reaction_amount,
    reaction_concentration,
    volume,
)


def test_no_external_species_in_nested_compartment():
    class Nested(Compartment):
        V: Volume = volume(default=1)
        A: Species = amount(default=1)

        eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)

    try:

        class Model(Compartment):
            V: Volume = volume(default=1)
            A: Species = amount(default=1)

            nested = Nested(A=A)
            eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)
    except TypeError:
        assert True
        return
    assert False


def test_external_ic_in_nested_compartment():
    class Nested(Compartment):
        V: Volume = volume(default=1)
        A: Species = amount(default=1)

        eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)

    class Model(Compartment):
        V: Volume = volume(default=1)
        A: Species = amount(default=1)

        nested = Nested(A=2)
        eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)

    assert Model.nested.A.initial == 2


def test_no_volume_in_compartment():
    try:

        class Model(Compartment):
            A: Species = amount(default=1)

            eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)
    except AttributeError:
        assert True
        return
    assert False


def test_more_than_one_volume_in_compartment():
    try:

        class Model(Compartment):
            V1: Volume = volume(default=1)
            V2: Volume = volume(default=1)
            A: Species = amount(default=1)

            eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)
    except AttributeError:
        assert True
        return
    assert False


def test_rate_law_with_amount():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=2)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = amount(default=1)
        B: Species = amount(default=2)
        AB: Species = amount(default=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_rate_law_with_concentration():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = concentration(default=1)
        B: Species = concentration(default=2)
        AB: Species = concentration(default=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_absolute_rate_law_with_amount():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = AbsoluteRateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = amount(default=1)
        B: Species = amount(default=2)
        AB: Species = amount(default=0)

        eq = AbsoluteRateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_absolute_rate_law_with_concentration():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = AbsoluteRateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1 / 2)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = concentration(default=1)
        B: Species = concentration(default=2)
        AB: Species = concentration(default=0)

        eq = AbsoluteRateLaw(reactants=[A, 2 * B], products=[AB], rate_law=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_mass_action_with_amount():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = RateLaw(
            reactants=[A, 2 * B], products=[AB], rate_law=(A / 2) * (B / 2) ** 2 * 2
        )

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = amount(default=1)
        B: Species = amount(default=2)
        AB: Species = amount(default=0)

        eq = MassAction(reactants=[A, 2 * B], products=[AB], rate=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_mass_action_with_concentration():
    class Model(System):
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=A * B**2)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        V: Volume = volume(default=2)
        A: Species = concentration(default=1)
        B: Species = concentration(default=2)
        AB: Species = concentration(default=0)

        eq = MassAction(reactants=[A, 2 * B], products=[AB], rate=1)

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))[["A", "AB", "B"]]
    assert np.all((result_1 == result_2).to_array().to_numpy())


def test_changing_volume():
    class Model(System):
        t: Independent = Independent()
        V: Parameter = assign(default=t**2 / 2 + 1)
        A: Variable = Variable(initial=1)
        B: Variable = Variable(initial=2)
        AB: Variable = Variable(initial=0)

        eq = RateLaw(reactants=[A, 2 * B], products=[AB], rate_law=A * B**2 / V)

    sim1 = Simulator(Model)
    result_1 = sim1.solve(save_at=np.linspace(0, 10, 10))

    class VolumeModel(Compartment):
        t: Independent = Independent()
        V: Volume = volume(default=1)
        A: Species = concentration(default=1)
        B: Species = concentration(default=2)
        AB: Species = concentration(default=0)

        eq = MassAction(reactants=[A, 2 * B], products=[AB], rate=1)
        vol_eq = V.derive() << t

    sim2 = Simulator(VolumeModel)
    result_2 = sim2.solve(save_at=np.linspace(0, 10, 10))
    calculated_volumes = np.linspace(0, 10, 10) ** 2 / 2 + 1
    volumes = np.asarray(result_2["V"])
    assert np.all(
        np.abs((result_1 - result_2[["A", "AB", "B"]]))
        <= (result_1 + result_2[["A", "AB", "B"]]) / 2 * 0.01
    )
    assert np.all(
        np.abs(calculated_volumes - volumes)
        <= (calculated_volumes + volumes) / 2 * 0.01
    )


def test_nested_compartments():
    class Nested(Compartment):
        V: Volume = volume(default=1)
        A: Species = amount(default=1)

        eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)

    class Model(Compartment):
        V: Volume = volume(default=1)
        A: Species = amount(default=1)

        nested = Nested()
        eq = RateLaw(reactants=[A], products=[2 * A], rate_law=1)

    sim = Simulator(Model)
    sim.solve(save_at=np.linspace(0, 10, 10))

    assert Model.A in sim.compiled.variables
    assert Model.nested.A in sim.compiled.variables
    assert Model._simbio_volume == Model.V
    assert Model.nested._simbio_volume == Model.nested.V


def test_species_in_reactant():
    class Nested(Compartment):
        V: Volume = Volume(initial=2)
        A: Reactant = reaction_amount(default=0.5)
        B: Reactant = reaction_concentration(default=2)
        AB: Reactant = reaction_concentration(default=0)

        eq = RateLaw(reactants=[A, B], products=[AB], rate_law=2)

    assert make_concentration(Nested.A.variable) == Nested.A.variable / Nested.V
    assert make_concentration(Nested.B.variable) == Nested.B.variable
    assert (
        compensate_volume(
            Nested.A.variable, rhs=2 * Nested.A.variable, reaction_is_concentration=True
        )
        == 2 * Nested.A.variable * Nested.V
    )
    assert (
        compensate_volume(
            Nested.B.variable, rhs=2 * Nested.B.variable, reaction_is_concentration=True
        )
        == 2 * Nested.B.variable
    )
    nsim = Simulator(Nested)
    nsim.solve(save_at=np.linspace(0, 10, 10))

    class Model(Compartment):
        V: Volume = Volume(initial=4)
        A: Reactant = reaction_amount(default=1)
        B: Reactant = reaction_concentration(default=3)
        nested = Nested()
        eq = MassAction(products=[A, B], reactants=[nested.AB], rate=1)

    sim = Simulator(Model)
    sim.solve(save_at=np.linspace(0, 10, 10))


def test_species_in_reactant_with_external_stoichiometry():
    class Nested(System):
        A: Reactant = reaction_initial(default=0.5)
        B: Reactant = reaction_initial(default=2)
        AB: Reactant = reaction_initial(default=0)

        eq = RateLaw(reactants=[A, B], products=[AB], rate_law=2)

    nsim = Simulator(Nested)
    nsim.solve(save_at=np.linspace(0, 10, 10))

    class Model(Compartment):
        V: Volume = Volume(initial=4)
        A: Reactant = reaction_amount(default=1)
        B: Reactant = reaction_concentration(default=3)
        nested = Nested(A=2 * A, B=3 * B)

        eq = MassAction(products=[nested.A, B], reactants=[nested.AB], rate=1)

    assert Model.nested.A.stoichiometry == 2
    assert Model.nested.B.stoichiometry == 3
    assert (
        make_concentration(Model.nested.A.variable) == Model.nested.A.variable / Model.V
    )
    assert make_concentration(Model.nested.B.variable) == Model.nested.B.variable
    assert (
        compensate_volume(
            Model.nested.A.variable,
            2 * Model.nested.A.variable,
            reaction_is_concentration=True,
        )
        == 2 * Model.nested.A.variable * Model.V
    )
    assert (
        compensate_volume(
            Model.nested.B.variable,
            2 * Model.nested.B.variable,
            reaction_is_concentration=True,
        )
        == 2 * Model.nested.B.variable
    )
    sim = Simulator(Model)
    sim.solve(save_at=np.linspace(0, 10, 10))
