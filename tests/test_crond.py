import pytest  # noqa: F401

from functools import partial
from time import sleep
from types import SimpleNamespace

from pgcooldown import CronD


def slupdate(slp, crond):
    sleep(slp)
    crond.update()


def update_x(x):
    x.value -= 1


x = SimpleNamespace(value=42)
crond = CronD()


def test_add():
    crond.add(1, partial(update_x, x))
    assert len(crond.heap) == 1


def test_run_once():
    slupdate(1.1, crond)
    crond.update()
    assert len(crond.heap) == 0
    assert x.value == 41


def test_repeated():
    cid = crond.add(1, partial(update_x, x), repeat=True)
    slupdate(1.1, crond)
    crond.update()
    assert len(crond.heap) == 1
    assert x.value == 40

    slupdate(1, crond)
    crond.update()
    assert len(crond.heap) == 1
    assert x.value == 39

    crond.remove(cid)
    assert len(crond.heap) == 0

    slupdate(1, crond)
    assert x.value == 39
