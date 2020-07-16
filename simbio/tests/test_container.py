from simbio.core import Container, Content
from ward import fixture, raises, test


@fixture
def data():
    main = Container("main", belongs_to=None)
    cont = main._add(Content("cont", belongs_to=main))
    sub = main._add(Container("sub", belongs_to=main))
    subcont = sub._add(Content("subcont", belongs_to=sub))
    return main, {"cont": cont, "sub": sub, "sub.subcont": subcont}


@test("Add content")
def _(data=data):
    main, _ = data

    # Not Content
    with raises(TypeError):
        main._add(1)

    # Name collision
    with raises(ValueError):
        main._add(Content("cont", belongs_to=main))
    main.sub._add(Content("cont", belongs_to=main.sub))  # Fine

    # Doesn't belong to Container
    with raises(Exception):
        main._add(Content("cont2", belongs_to=None))

    with raises(Exception):
        main.sub._add(Content("cont2", belongs_to=main))


@test("View of content")
def _(data=data):
    main, d = data
    assert main.contents == d
    assert d["sub"].contents == {"subcont": d["sub.subcont"]}


@test("Relative name")
def _(data=data):
    main, d = data

    for name, content in d.items():
        assert main._relative_name(content) == name

    cont, sub, subcont = d["cont"], d["sub"], d["sub.subcont"]

    assert sub._relative_name(subcont) == "subcont"

    # Cont is not in sub
    with raises(AttributeError):
        sub._relative_name(cont)

    # Not implemented for self
    for c in (main, sub):
        with raises(NotImplementedError):
            c._relative_name(c)


@test("Contains")
def _(data=data):
    main, d = data

    for v in d.values():
        assert v in main

    assert d["sub.subcont"] in d["sub"]

    assert d["cont"] not in d["sub"]

    # Self is not contained
    assert main not in main

    # Not Content
    assert 1 not in main


@test("Get item or attribute")
def _(data=data):
    main, d = data

    # All from main container
    for name, content in d.items():
        assert main[name] == content
        assert getattr(main, name) == content

    # All from sub container
    sub, subcont = d["sub"], d["sub.subcont"]
    assert sub["subcont"] == subcont
    assert getattr(sub, "subcont") == subcont

    with raises(AttributeError):
        getattr(main, "not_here")

    with raises(KeyError):
        sub["not_here"]

    # Tries getting attribute of Content
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
