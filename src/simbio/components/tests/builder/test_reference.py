from simbio.components import EmptyCompartment, Parameter, Species
from simbio.components._container import Reference
from simbio.reactions.single import Creation


class Model(EmptyCompartment):
    A: Species = 1
    k: Parameter = 1
    create_A = Creation(A=A, rate=k)


def test_contents_are_references():
    assert isinstance(Model.A, Reference)
    assert isinstance(Model.k, Reference)
    assert isinstance(Model.create_A.A, Reference)
    assert isinstance(Model.create_A.rate, Reference)


def test_containers_are_not_references():
    assert not isinstance(Model, Reference)
    assert not isinstance(Model.create_A, Reference)


def test_resolve_reference():
    assert Model.A != Model.create_A.A
    assert Model.k != Model.create_A.rate

    assert Model.A.resolve() == Model.create_A.A.resolve(recursive=True)
    assert Model.k.resolve() == Model.create_A.rate.resolve(recursive=True)
