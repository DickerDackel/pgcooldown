import pytest

from time import sleep
from pgcooldown import Cooldown, LerpThing


def test_cooldown():
    lt = LerpThing(0, 0, 1)
    assert isinstance(lt.duration, Cooldown)

    cd = Cooldown(1)
    lt = LerpThing(0, 0, cd)
    assert lt.duration is cd


def test_no_repeat():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=0)
    sleep(1.2)
    assert lt.v == 0


def test_repeat():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=1)
    sleep(1.2)
    assert round(lt.v, 1) == 0.8


def test_bounce():
    lt = LerpThing(vt0=1, vt1=0, duration=1, repeat=2)
    sleep(1.2)
    assert round(lt.duration.temperature, 1) == -0.2
    assert round(lt.v, 1) == 0.2


def test_easing():
    lt = LerpThing(vt0=1, vt1=0, duration=1, ease=lambda x: 1 - x)
    sleep(0.2)
    assert round(lt.v, 1) == 0.2


if __name__ == '__main__':
    test_no_repeat()
    test_repeat()
    test_bounce()
    test_easing()
