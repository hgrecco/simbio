from simbio.core import Container, Content
from ward import fixture, raises, test


@fixture
def data():
    main = Container(name="main")
    cont = main._add(Content(name="cont"))
    sub = main._add(Container(name="sub"))
    subcont = sub._add(Content(name="subcont"))

    return main, {"cont": cont, "sub": sub, "sub.subcont": subcont}


@test("Add content")
def _(data=data):
    main, _ = data

    # Not Content
    with raises(TypeError):
        main._add(1)

    # Belongs to other Container
    with raises(Exception):
        main.sub._add(main.cont)

    # Name collision
    cont = Content(name="cont")
    with raises(ValueError):
        main._add(cont)

    main.sub._add(cont)  # Fine


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

    assert new_main.name == main.name
    assert new_main.parent is None

    for new_c in new_main._contents.values():
        assert new_c.parent is new_main

    for c, new_c in zip(main.contents.values(), new_main.contents.values()):
        assert new_c.name == c.name
        assert new_c is not c
        assert new_c.parent.name == c.parent.name
        assert (new_c.parent is new_main) or (new_c.parent in new_main)


@test("Absolute path")
def _(data=data):
    main, _ = data

    assert main.cont._absolute_path() == [main, main.cont]
    assert main.sub.subcont._absolute_path() == [main, main.sub, main.sub.subcont]


@test("Common parent")
def _(data=data):
    main, _ = data

    assert Content._common_parent(main.cont, main.sub) == main
    assert Content._common_parent(main.cont, main.sub.subcont) == main
    assert Content._common_parent(main.sub, main.sub.subcont) == main.sub
