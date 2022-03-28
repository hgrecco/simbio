"""
Test model equivalence for Species and Parameters.
"""

from simbio.model import Compartment, Parameter, Species


def test_same_value():
    class ModelA(Compartment):
        A: Species = 0

    class ModelB(Compartment):
        A: Species = 0

    assert ModelA == ModelB


def test_same_parameter():
    class ModelA(Compartment):
        k: Parameter = 0
        A: Species = k

    class ModelB(Compartment):
        k: Parameter = 0
        A: Species = k

    assert ModelA == ModelB


def test_diff_value():
    class ModelA(Compartment):
        A: Species = 0

    class ModelB(Compartment):
        A: Species = 1

    assert ModelA != ModelB


def test_diff_parameter_value():
    class ModelA(Compartment):
        k: Parameter = 0
        A: Species = k

    class ModelB(Compartment):
        k: Parameter = 1
        A: Species = k

    assert ModelA != ModelB


def test_diff_name():
    """As only the name is different, they are equivalent models, but not equal.

    The combined model should have two species: A and B.
    """

    class ModelA(Compartment):
        A: Species = 0

    class ModelB(Compartment):
        B: Species = 0

    assert ModelA != ModelB


def test_diff_parameter_name():
    """As only the parameter name is different, they are equivalent models, but not equal.

    The combined model should have two parameters, kA and kB, and one species, A.
    But, should A be linked to parameter kA or kB?
    """

    class ModelA(Compartment):
        kA: Parameter = 0
        A: Species = kA

    class ModelB(Compartment):
        kB: Parameter = 0
        A: Species = kB

    assert ModelA != ModelB


def test_value_vs_parameter():
    """Although the parameter has the same value and they are equivalent models,
    they are not equal.

    In principle, Parameter `k` could be later used in another Component,
    linking Species `A` value to that other Component.

    Should the combined model have:
        1. A: Species = 0
        2. A: Species = k
    """

    class ModelA(Compartment):
        A: Species = 0

    class ModelB(Compartment):
        k: Parameter = 0
        A: Species = k

    assert ModelA != ModelB
