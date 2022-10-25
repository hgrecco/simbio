from .._container import Container, Reference


class MyContainer(Container):
    def __init__(self):
        self._contents = {}

    def add(self, name, value):
        if isinstance(value, Container):
            value.name = name
            value.parent = self
        elif isinstance(value, Reference):
            value = value.relative_to(self)
        self._contents[name] = value

    def __repr__(self):
        return self.name


top = MyContainer()
top.add("my_int", 1)

top.add("level1", MyContainer())
top.level1.add("my_float", 1.0)

top.level1.add("level2", MyContainer())
top.level1.level2.add("my_str", "hola")


def test_getattr():
    for x in (top.my_int, top.level1.my_float, top.level1.level2.my_str):
        assert isinstance(x, Reference)

    for x in (top.level1, top.level1.level2):
        assert isinstance(x, Container)
        assert not isinstance(x, Reference)


def test_relative_reference_parent():
    containers = (top, top.level1, top.level1.level2)

    for i, c in enumerate(containers):
        assert top.my_int.relative_to(c).parent == i

    for i, c in enumerate(containers, start=-1):
        assert top.level1.my_float.relative_to(c).name.lstrip(".").count(".") == abs(
            min(i, 0)
        )
        assert top.level1.my_float.relative_to(c).parent == max(i, 0)
