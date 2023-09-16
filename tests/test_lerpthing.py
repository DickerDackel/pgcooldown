import pytest

from time import sleep
from pgcooldown import Cooldown, LerpThing, AutoLerpThing
from pytest import approx


def test_cooldown():
    lt = LerpThing(0, 0, 1)
    assert isinstance(lt.duration, Cooldown)

    cd = Cooldown(1)
    lt = LerpThing(0, 0, cd)
    assert lt.duration is cd

    # duration = 0 always returns vt0
    lt = LerpThing(1, 2, 0)
    assert lt() == 1


def test_call_is_v():
    lt = LerpThing(0, 1, 1)
    sleep(0.5)
    assert approx(lt(), 0.01) == approx(lt(), 0.01)


def test_no_repeat():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=0)
    sleep(1.2)
    assert lt() == 0


def test_repeat():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=1)
    sleep(1.2)
    assert approx(lt(), 0.01) == 0.8


def test_bounce():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=2)
    sleep(1.2)
    assert approx(lt(), 0.01) == 0.2


def test_easing():
    lt = LerpThing(vt0=1, vt1=0, duration=1, ease=lambda x: 1 - x)
    sleep(0.2)
    assert approx(lt(), 0.01) == 0.2


def test_finished():
    lt = LerpThing(0, 1, 0.9)
    sleep(1)
    assert lt.finished()


def test_descriptor():
    class X:
        lt = AutoLerpThing()

        def __init__(self):
            self.lt = (0, 10, 1)

    x = X()
    assert approx(x.lt, 0.01) == 0
    sleep(0.1)
    assert approx(x.lt, rel=0.1) == 1
    sleep(1)
    assert x.lt == 10


if __name__ == '__main__':
    test_cooldown()
    test_call_is_v()
    test_no_repeat()
    test_repeat()
    test_bounce()
    test_easing()
    test_finished()
    test_descriptor()
