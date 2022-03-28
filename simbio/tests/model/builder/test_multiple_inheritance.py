from pytest import raises
from simbio.model import Compartment, Species


def test_disjoint():
    """Inheriting from disjoint models
    results in the union of the models.
    """

    class ModelA(Compartment):
        A: Species = 0

    class ModelB(Compartment):
        B: Species = 0

    class Joint(ModelA, ModelB):
        pass

    assert Joint > ModelA
    assert Joint > ModelB

    assert Joint.A == ModelA.A
    assert Joint.B == ModelB.B


def test_non_colliding():
    """Inheriting from models whose name collides
    but their respective values are equal
    results in the union of the models.
    """

    class ModelA(Compartment):
        C: Species = 0

    class ModelB(Compartment):
        C: Species = 0

    class Joint(ModelA, ModelB):
        pass

    assert Joint == ModelA
    assert Joint == ModelB


def test_colliding():
    """Inheriting from models that collide
    requires overriding values to eliminate collisions.
    """

    class ModelA(Compartment):
        C: Species = 0

    class ModelB(Compartment):
        C: Species = 1

    with raises(ValueError):

        class CollidingJoint(ModelA, ModelB):
            pass

    class Joint(ModelA(C=1), ModelB):
        pass

    assert Joint != ModelA
    assert Joint == ModelB
