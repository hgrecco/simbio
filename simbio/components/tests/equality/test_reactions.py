"""
Test model equivalence for Reactions.
"""

from simbio.components import EmptyCompartment, Parameter, Species
from simbio.reactions.single import Creation


def test_same_reaction():
    # Both Species and Parameter are internal
    class ModelA(EmptyCompartment):
        create_A = Creation(A=0, rate=0)

    class ModelB(EmptyCompartment):
        create_A = Creation(A=0, rate=0)

    assert ModelA == ModelB

    # External Species and internal Parameter
    class ModelA(EmptyCompartment):
        A: Species = 0
        create_A = Creation(A=A, rate=0)

    class ModelB(EmptyCompartment):
        A: Species = 0
        create_A = Creation(A=A, rate=0)

    assert ModelA == ModelB

    # Internal Species and external Parameter
    class ModelA(EmptyCompartment):
        k: Parameter = 0
        create_A = Creation(A=0, rate=k)

    class ModelB(EmptyCompartment):
        k: Parameter = 0
        create_A = Creation(A=0, rate=k)

    assert ModelA == ModelB


def test_diff_value():
    # Different internal Species
    class ModelA(EmptyCompartment):
        create_A = Creation(A=0, rate=0)

    class ModelB(EmptyCompartment):
        create_A = Creation(A=1, rate=0)

    assert ModelA != ModelB

    # Different internal Parameter
    class ModelA(EmptyCompartment):
        create_A = Creation(A=0, rate=0)

    class ModelB(EmptyCompartment):
        create_A = Creation(A=0, rate=1)

    assert ModelA != ModelB

    # Different external Species
    class ModelA(EmptyCompartment):
        A: Species = 0
        create_A = Creation(A=A, rate=0)

    class ModelB(EmptyCompartment):
        A: Species = 1
        create_A = Creation(A=A, rate=0)

    assert ModelA != ModelB

    # Different external Parameter
    class ModelA(EmptyCompartment):
        k: Parameter = 0
        create_A = Creation(A=0, rate=k)

    class ModelB(EmptyCompartment):
        k: Parameter = 1
        create_A = Creation(A=0, rate=k)

    assert ModelA != ModelB


def test_diff_name():
    """As only the name is different, they are equivalent models, but not equal.

    The combined model should have two reactions: create_A and create_B.
    """

    class ModelA(EmptyCompartment):
        create_A = Creation(A=0, rate=0)

    class ModelB(EmptyCompartment):
        create_B = Creation(A=0, rate=0)

    assert ModelA != ModelB


def test_diff_component_name():
    """As only the component name is different, they are equivalent models, but not equal.

    The combined model should have two components, A and B, and one reaction, create.
    But, should create be linked to component A or B?
    """

    # Different external Species
    class ModelA(EmptyCompartment):
        A: Species = 0
        create = Creation(A=A, rate=0)

    class ModelB(EmptyCompartment):
        B: Species = 0
        create = Creation(A=B, rate=0)

    assert ModelA != ModelB

    # Different external Parameter
    class ModelA(EmptyCompartment):
        A: Parameter = 0
        create = Creation(A=0, rate=A)

    class ModelB(EmptyCompartment):
        B: Parameter = 0
        create = Creation(A=0, rate=B)

    assert ModelA != ModelB


def test_value_vs_component():
    """Although the component has the same value and they are equivalent models,
    they are not equal.

    In principle, component `A` could be later used in another Component or Reaction,
    linking component `A` value to that other Component.

    Should the combined model have:
        1. create = Reaction(component=0)  # internal
        2. create = Reaction(component=A)  # external
    """

    # All internal
    class Model(EmptyCompartment):
        create = Creation(A=0, rate=0)

    # External Species
    class ModelA(EmptyCompartment):
        A: Species = 0
        create = Creation(A=A, rate=0)

    # External Parameter
    class ModelB(EmptyCompartment):
        A: Parameter = 0
        create = Creation(A=0, rate=A)

    assert Model != ModelA
    assert Model != ModelB
    assert ModelA != ModelB
