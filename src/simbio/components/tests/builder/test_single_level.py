from pytest import raises

from simbio.components import EmptyCompartment, Parameter, Species
from simbio.reactions.single import Creation


def test_dynamic_vs_static():
    """Creating a single-level model statically and dynamically.

    Uses free and dependent parameters.
    """

    class Static(EmptyCompartment):
        k_free: Parameter = 1
        k_dep: Parameter = k_free
        A: Species = 0
        B: Species = k_free
        create_A = Creation(A=A, rate=1)
        create_B = Creation(A=B, rate=k_dep)

    Dynamic = EmptyCompartment.to_builder()
    k_free = Dynamic.add_parameter("k_free", 1)
    k_dep = Dynamic.add_parameter("k_dep", k_free)
    A = Dynamic.add_species("A", 0)
    B = Dynamic.add_species("B", k_free)
    Dynamic.add_reaction("create_A", Creation(A=A, rate=1))
    Dynamic.add_reaction("create_B", Creation(A=B, rate=k_dep))
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_add_external_species():
    # Dynamically, we could check if X is a number | Parameter.

    X = Species(0)

    with raises(TypeError):

        class Static(EmptyCompartment):
            A: Species = X

    Dynamic = EmptyCompartment.to_builder()
    with raises(TypeError):
        Dynamic.add_species("A", X)


def test_add_external_parameter():
    # Dynamically, we could check if it already exists inside the Compartment.

    X = Parameter(0)

    with raises(TypeError):

        class Static(EmptyCompartment):
            k: Parameter = X

    Dynamic = EmptyCompartment.to_builder()
    with raises(TypeError):
        Dynamic.add_parameter("k", X)


def test_use_external_species():
    # Check if it already exists inside the Compartment.

    X = Species(0)

    with raises(TypeError):

        class Static(EmptyCompartment):
            create = Creation(A=X, rate=1)

    Dynamic = EmptyCompartment.to_builder()
    with raises(TypeError):
        Dynamic.add_reaction("create", Creation(A=X, rate=1))


def test_use_external_parameter():
    # Check if it already exists inside the Compartment.

    X = Parameter(0)

    with raises(TypeError):

        class Static(EmptyCompartment):
            k: Parameter = X

    with raises(TypeError):

        class Static(EmptyCompartment):  # noqa: F811
            A: Species = X

    with raises(TypeError):

        class Static(EmptyCompartment):  # noqa: F811
            create = Creation(A=0, rate=X)

    Dynamic = EmptyCompartment.to_builder()
    with raises(TypeError):
        Dynamic.add_parameter("k", X)
    with raises(TypeError):
        Dynamic.add_species("A", X)
    with raises(TypeError):
        Dynamic.add_reaction("create", Creation(A=0, rate=X))


def test_use_component_from_external_compartment():
    class External(EmptyCompartment):
        A: Species = 0
        k: Parameter = 0

    # Species
    with raises(ValueError):

        class Static(EmptyCompartment):
            A: Species = 1
            create_A = Creation(A=External.A, rate=1)

    Dynamic = EmptyCompartment.to_builder()
    Dynamic.add_species("A", 1)
    with raises(ValueError):
        Dynamic.add_reaction("create", Creation(A=External.A, rate=1))

    # Parameter
    with raises(ValueError):

        class Static(EmptyCompartment):  # noqa: F811
            k: Parameter = 1
            A: Species = External.k

    Dynamic = EmptyCompartment.to_builder()
    Dynamic.add_parameter("k", 1)
    with raises(ValueError):
        Dynamic.add_species("A", External.k)
