import pytest

from pytest import approx
from pgcooldown import Cooldown, LerpThing
from time import sleep


def test_init():
    c = Cooldown(1)
    assert c.duration == 1
    assert c.paused is False
    assert c.remaining() >= 0

    c = Cooldown(1, cold=True)
    assert c.duration == 1
    assert c.remaining() == 0
    assert c.cold()
    assert not c.hot()

    c = Cooldown(0)
    assert c.cold()
    assert c.remaining() == 0
    assert not c.hot()

    c = Cooldown(10, paused=True)
    assert c.paused
    assert c.remaining() == 10
    c.start()
    sleep(1)
    assert approx(c.remaining(), abs=0.01) == c.duration - 1


def test_repr():
    c = Cooldown(10)
    assert repr(c) == 'Cooldown(duration=10.0, cold=False, paused=False)'


def test_cold():
    c = Cooldown(0.1)
    sleep(0.2)
    assert c.cold()

    c = Cooldown(1)
    c.set_cold(True)
    assert c.cold()
    assert not c.hot()
    assert c.duration == 1


def test_reset():
    c = Cooldown(1)
    sleep(2)
    assert c.remaining() == 0
    assert c.cold()
    assert not c.hot()
    assert not c.paused

    c.reset(2)
    assert approx(c.duration, abs=0.01) == 2
    assert approx(c.remaining(), abs=0.01) == c.duration
    assert not c.cold()
    assert c.hot()
    assert not c.paused


def test_wrap():
    c = Cooldown(1)
    sleep(1.5)
    assert c.remaining() == 0
    assert c.temperature() < 0
    c.reset(wrap=True)
    assert approx(c.temperature(), abs=0.01) == 0.5


def test_remaining():
    c = Cooldown(0.1)
    assert approx(c.remaining(), abs=0.01) == 0.1
    sleep(0.05)
    assert approx(c.remaining(), abs=0.01) == 0.05
    sleep(0.1)
    assert c.remaining() == 0
    assert approx(c.temperature(), abs=0.01) == -0.05
    c.reset(1)
    sleep(0.5)
    c.set_to(1)
    assert approx(c.remaining(), abs=0.01) == 1


def test_set_to():
    c = Cooldown(1)
    with pytest.raises(ValueError) as e:
        c.set_to(2)
    assert e.type is ValueError
    assert 'Cannot set remaining' in str(e.value)
    assert approx(c.remaining(), abs=0.01) == 1


def test_pause():
    c = Cooldown(5).pause()
    assert approx(c.remaining(), abs=0.01) == 5
    sleep(1)
    assert approx(c.remaining(), abs=0.01) == 5
    c.start()
    sleep(1)
    c.pause()
    assert approx(c.remaining(), abs=0.01) == 4
    sleep(1)
    assert approx(c.remaining(), abs=0.01) == 4
    c.start()
    sleep(1)
    assert approx(c.remaining(), abs=0.01) == 3
    c.reset()
    c.pause()
    c.set_to(4.1)
    assert c.remaining() == 4.1
    c.start()
    sleep(0.1)
    assert approx(c.remaining(), abs=0.01) == 4


def test_normalized():
    c = Cooldown(4)
    # Multiply by 100 gives us more leeway to cope with load impact
    assert approx(c.normalized() * 100, abs=0.1) == 0
    sleep(1)
    assert approx(c.normalized() * 100, abs=0.1) == 25
    sleep(1)
    assert approx(c.normalized() * 100, abs=0.1) == 50
    sleep(1)
    assert approx(c.normalized() * 100, abs=0.1) == 75
    sleep(1)
    assert approx(c.normalized() * 100, abs=0.1) == 100
    assert c.cold()


def test_copyconstructor():
    c = Cooldown(10).pause()
    d = Cooldown(c)
    assert d.duration == 10
    assert d.paused is False


def test_compare():
    c = Cooldown(10, paused=True)
    assert c == 10
    assert c > 5
    assert c >= 10
    assert c < 15
    assert c <= 10
    assert c != 5
    assert bool(c)
    assert int(c) == 10
    assert float(c) == 10.0


if __name__ == '__main__':
    test_init()
    test_repr()
    test_cold()
    test_reset()
    test_wrap()
    test_remaining()
    test_set_to()
    test_pause()
    test_normalized()
    test_copyconstructor()
    test_compare()
