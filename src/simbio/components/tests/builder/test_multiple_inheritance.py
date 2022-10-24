from pytest import raises

from simbio.components import EmptyCompartment, Override, Species


def test_disjoint():
    """Inheriting from disjoint models
    results in the union of the models.
    """

    class ModelA(EmptyCompartment):
        A: Species = 0

    class ModelB(EmptyCompartment):
        B: Species = 0

    class Joint(ModelA, ModelB):
        pass

    # assert Joint > ModelA
    # assert Joint > ModelB

    assert Joint.A.resolve() == ModelA.A.resolve()
    assert Joint.B.resolve() == ModelB.B.resolve()


def test_non_colliding():
    """Inheriting from models whose name collides
    but their respective values are equal
    results in the union of the models.
    """

    class ModelA(EmptyCompartment):
        C: Species = 0

    class ModelB(EmptyCompartment):
        C: Species = 0

    class Joint(ModelA, ModelB):
        pass

    assert Joint == ModelA
    assert Joint == ModelB


def test_colliding():
    """Inheriting from models that collide
    requires overriding values to eliminate collisions.
    """

    class ModelA(EmptyCompartment):
        C: Species = 0

    class ModelB(EmptyCompartment):
        C: Species = 1

    with raises(ValueError):

        class CollidingJoint(ModelA, ModelB):
            pass

    class Joint(ModelA, ModelB):
        C: Species[Override] = 1

    assert Joint != ModelA
    assert Joint == ModelB
