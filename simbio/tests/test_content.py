from simbio.compartments import Compartment
from simbio.core import Container, Content
from simbio.parameters import Parameter
from simbio.reactants import Reactant
from ward import each, raises, test, xfail
from ward.fixtures import fixture

classes = (Content, Container, Reactant, Parameter, Compartment)


@test("Set or del protected attributes in {cls.__name__}")
def _(cls=each(*classes)):
    instance = cls(name="name", belongs_to=None)

    with raises(AttributeError):
        instance.name = "new_name"

    with raises(AttributeError):
        instance.belongs_to = "new_container"

    with raises(AttributeError):
        del instance.name

    with raises(AttributeError):
        del instance.belongs_to


@test("{cls.__name__}.name must be valid Python identifier")
def _(cls=each(*classes)):
    for name in ("name.", "1name"):
        with raises(ValueError):
            cls(name="name.", belongs_to=None)


@xfail("Not implemented yet")
@test("{cls.__name__}.name must not collide with Simbio methods and attributes")
def _(cls=each(*classes)):
    colliding_name = "name"
    with raises(ValueError):
        cls(name=colliding_name, belongs_to=None)


@test("Add content")
def _():
    main = Container("main", belongs_to=None)
    main.add(Content("cont", belongs_to=main))

    # Not Content
    with raises(TypeError):
        main.add(1)

    # Name collision
    with raises(ValueError):
        main.add(Content("cont", belongs_to=main))

    # Doesn't belong to Container
    with raises(Exception):
        main.add(Content("cont2", belongs_to=None))


@fixture
def data():
    main = Container("main", belongs_to=None)
    cont = main.add(Content("cont", belongs_to=main))
    sub = main.add(Container("sub", belongs_to=main))
    subcont = sub.add(Content("subcont", belongs_to=sub))
    return main, {"cont": cont, "sub": sub, "sub.subcont": subcont}


@test("View of content")
def _(data=data):
    main, d = data
    assert main.contents == d
    assert d["sub"].contents == {"subcont": d["sub.subcont"]}


@test("Relative name")
def _(data=data):
    main, d = data

    for name, content in d.items():
        assert main.relative_name(content) == name

    cont, sub, subcont = d["cont"], d["sub"], d["sub.subcont"]

    assert sub.relative_name(subcont) == "subcont"

    # Cont is not in sub
    with raises(AttributeError):
        sub.relative_name(cont)

    # Not implemented for self
    for c in (main, sub):
        with raises(NotImplementedError):
            c.relative_name(c)


@test("Get item or attribute")
def _(data=data):
    main, d = data

    for name, content in d.items():
        assert main[name] == content
        assert getattr(main, name) == content

    sub, subcont = d["sub"], d["sub.subcont"]

    assert sub["subcont"] == subcont
    assert getattr(sub, "subcont") == subcont

    with raises(AttributeError):
        getattr(main, "not_here")

    with raises(KeyError):
        sub["not_here"]

    with raises(TypeError):
        main["sub.subcont.not_here"]


@test("Copy container")
def _(data=data):
    main, d = data

    new_main = main.copy()

    for c, nc in zip(main.contents.values(), new_main.contents.values()):
        assert c.name == nc.name
        assert c.belongs_to.name == nc.belongs_to.name
        assert c is not nc
        assert c.belongs_to is not nc.belongs_to
