from itertools import combinations

from simbio import Compartment, Parameter, Species
from ward import each, raises, test


@test("{cls.__name__} equality")
def _(cls=each(Parameter, Species)):
    instance = cls(1, name="name")

    assert cls(1, name="name") is not instance
    assert cls(1, name="name") == instance

    assert cls(2, name="name") != instance
    assert cls(1, name="other_name") != instance


@test("Species binding")
def _():
    class Model(Compartment):
        A = Species(0)

        class SubModel(Compartment):
            A = Species(0)

            class SubSubModel(Compartment):
                A = Species(0)

    class OtherModel(Compartment):
        A = Species(0)

    X = (Model.A, Model.SubModel.A, Model.SubModel.SubSubModel.A)

    for x in X:
        assert (x & x).parent == x.parent

        with raises(ValueError):
            x & OtherModel.A

    for x, y in combinations(X, 2):
        xy = x & y
        assert xy.parent == x.parent
        assert xy.parent[xy.name] == xy
