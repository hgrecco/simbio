from simbio import Parameter, Species
from ward import each, test


@test("{cls.__name__} equality")
def _(cls=each(Parameter, Species)):
    instance = cls(1, name="name")

    assert cls(1, name="name") is not instance
    assert cls(1, name="name") == instance

    assert cls(2, name="name") != instance
    assert cls(1, name="other_name") != instance
