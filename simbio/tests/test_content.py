from simbio.core import Container, Content
from ward import each, raises, test, xfail

classes = (Content, Container)


@test("Set or del protected attributes in {cls.__name__}")
def _(cls=each(*classes)):
    instance = cls(name="fixed_name")

    for attr in ("name", "parent"):
        with raises(AttributeError):
            setattr(instance, attr, "new_name")

        with raises(AttributeError):
            delattr(instance, attr)


@test("Hash and equality by id in {cls.__name__}")
def _(cls=each(*classes)):
    obj1 = cls(name="name")
    obj2 = cls(name="name")

    assert hash(obj1) == id(obj1)
    assert obj1 == obj1
    assert obj1 != obj2


@test("Copy {cls.__name__}")
def _(cls=each(*classes)):
    orig_obj = cls(name="name")
    orig_obj.__parent = "parent"

    copy_obj = orig_obj.copy()
    # Different object with same name but no parent.
    assert copy_obj is not orig_obj
    assert copy_obj.name == orig_obj.name
    assert copy_obj.parent is None


@xfail("Not implemented yet")
@test("{cls.__name__}.name must not collide with Simbio methods and attributes")
def _(cls=each(*classes)):
    colliding_name = "name"
    with raises(ValueError):
        cls(name=colliding_name)
