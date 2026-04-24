import pytest

# from pytest import approx
from pgcooldown import lerp, invlerp, remap


def test_lerp():
    assert lerp(0.0, 1.0, 0.0) == 0.0
    assert lerp(0.0, 1.0, 0.5) == 0.5
    assert lerp(0.0, 1.0, 1.0) == 1.0

    with pytest.raises(TypeError) as e:
        lerp(0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        lerp('xyzzy', 1.0, 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        lerp(0.0, 'xyzzy', 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        lerp(0.0, 1.0, 'xyzzy')

    assert e.type is TypeError


def test_invlerp():
    assert invlerp(0.0, 1.0, 0.0) == 0.0
    assert invlerp(0.0, 1.0, 0.5) == 0.5
    assert invlerp(0.0, 1.0, 1.0) == 1.0

    with pytest.raises(ValueError) as e:
        invlerp(0.0, 0.0, 1.0)
    assert e.type is ValueError

    with pytest.raises(TypeError) as e:
        invlerp(0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        invlerp('xyzzy', 1.0, 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        invlerp(0.0, 'xyzzy', 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        invlerp(0.0, 1.0, 'xyzzy')
    assert e.type is TypeError


def test_remap():
    assert remap(0.0, 1.0, 0.0, 10.0, 0.0) == 0.0
    assert remap(0.0, 1.0, 0.0, 10.0, 0.5) == 5.0
    assert remap(0.0, 1.0, 0.0, 10.0, 1.0) == 10.0

    with pytest.raises(TypeError) as e:
        remap(0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        remap('xyzzy', 1.0, 0.0, 10.0, 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        remap(0.0, 'xyzzy', 0.0, 10.0, 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        remap(0.0, 1.0, 'xyzzy', 10.0, 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        remap(0.0, 1.0, 0.0, 'xyzzy', 0.0)
    assert e.type is TypeError

    with pytest.raises(TypeError) as e:
        remap(0.0, 1.0, 0.0, 10.0, 'xyzzy')
    assert e.type is TypeError
