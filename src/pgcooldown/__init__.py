"""Cooldown & co...

This module started with just the Cooldown class, which can be used check if a
specified time has passed.  It is mostly indended to be used to control
objects in a game loop, but it is general enough for other purposes as well.

    fire_cooldown = Cooldown(1, cold=True)
    while True:
        if fire_shot and fire_cooldown.cold():
            fire_cooldown.reset()
            launch_bullet()

        ...

With the usage of Cooldown on ramp data (e.g. a Lerp between an opaque and a
fully transparent sprite over the time of n seconds), I came up with the
LerpThing.  The LerpThing gives you exactly that.  A lerp between `from` and
`to` mapped onto a `duration`.

    alpha = LerpThing(0, 255, 5)
    while True:
        ...
        sprite.set_alpha(alpha())
        # or sprite.set_alpha(alpha.v)

        if alpha.finished:
            sprite.kill()

Finally, the need to use Cooldown for scheduling the creations of game
objects, the CronD class was added.  It schedules functions to run after a
wait period.

Note, that CronD doesn't do any magic background timer stuff, it needs to be
updated in the game loop.

    crond = CronD()
    crond.add(1, create_enemy(screen.center))
    crond.add(2, create_enemy(screen.center))
    crond.add(3, create_enemy(screen.center))
    crond.add(4, create_enemy(screen.center))

    while True:
        ...
        crond.update()

"""

import heapq
import weakref

from weakref import ReferenceType

from dataclasses import dataclass, field, InitVar
from typing import Callable, Self, Type

from pgcooldown._pgcooldown import Cooldown, lerp, invlerp, remap  # noqa: F401

__all__ = ['Cooldown', 'lerp', 'invlerp', 'remap', 'LerpThing',
           'AutoLerpThing', 'CronJob', 'CronD']


@dataclass
class LerpThing:
    """A time based generic gauge that lerps between 2 points.

    This class can be used for scaling, color shifts, momentum, ...

    It gets initialized with 2 Values for t0 and t1, and a time `duration`,
    then it lerps between these values.

    Once the time runs out, the lerp can stop, repeat from start or bounce back
    and forth.

    An optional easing function can be put on top of `t`.

    Parameters
    ----------
    vt0,
    vt1: [int | float]
        The endpoints of the lerp at `t == 0` and `t == 1`

    duration: Cooldown
        The length of the lerp.  This duration is mapped onto the range 0 - 1
        as `t`.

        This is a Cooldown object, so all configuration and query options
        apply, if you want to modify the lerp during its runtime.

        Note: If duration is 0, vt0 is always returned.

    ease: callable = lambda x: x
        An optional easing function to put over t

    repeat: int = 0
        After the duration has passed, how to proceed?

            0: Don't repeat, just stop transmogrifying
            1: Reset and repeat from start
            2: Bounce back and forth.  Note, that bounce back is implemented by
               swapping vt0 and vt1.

    loops: int = -1
        Limit the number of loops

    """
    vt0: float
    vt1: float
    duration: InitVar[Cooldown | float]
    ease: Callable[[float], float] = lambda x: x
    repeat: int = 0
    loops: int = -1

    def __post_init__(self, duration: Cooldown | float) -> None:
        self.duration = duration if isinstance(duration, Cooldown) else Cooldown(duration)
        self.loops -= 1

        # This is a special case.  We return vt1 when the cooldown is cold, but
        # if duration is 0, we're already cold right from the start, so it's
        # more intuitive to return the start value.
        # vt1 can be overwritten in that case, since we never will have a `t`
        # different from 0.
        #
        # While setting `duration` to 0 makes no sense in itself, it might
        # still be useful, if one wants to keep using the interface of the
        # LerpThing, but with a lerp that is basically a constant.
        #
        # Setting this here once is faster than doing it on every call.
        if duration == 0:
            self.vt1 = self.vt0

    def __call__(self) -> float:
        """Return the current lerped value"""
        # Note: Using cold precalculated instead of calling it twice, gave a
        # 30% speed increase!
        #
        # Note 2: Using both cold() on top and `duration.normalized` further
        # below created a race condition. All timing data needs to be fetched
        # atomically on top

        t = self.duration.normalized

        if t >= 1.0 and self.repeat:
            if  self.loops == 0:
                return self.vt1

            self.loops -= 1

            if self.repeat == 2:
                self.vt0, self.vt1 = self.vt1, self.vt0

            self.duration.reset(wrap=True)
            t = self.duration.normalized

        if t < 1.0:
            return lerp(self.vt0, self.vt1, self.ease(t))

        return self.vt1

    def __hash__(self) -> int: return id(self)  # noqa: E704
    def __bool__(self) -> bool: return bool(self())  # noqa: E704
    def __int__(self) -> int: return int(self())  # noqa: E704
    def __float__(self) -> float: return float(self())  # noqa: E704
    def __lt__(self, other: object) -> bool: return self() < other  # noqa: E704
    def __le__(self, other: object) -> bool: return self() <= other  # noqa: E704
    def __eq__(self, other: object) -> bool: return self() == other  # noqa: E704
    def __ne__(self, other: object) -> bool: return self() != other  # noqa: E704
    def __ge__(self, other: object) -> bool: return self() >= other  # noqa: E704
    def __gt__(self, other: object) -> bool: return self() > other  # noqa: E704

    def finished(self) -> bool:
        """Check if the LerpThing is done."""
        cold = self.duration.cold()
        return ((cold and not self.repeat)
                or (cold and self.repeat and not self.loops))


class AutoLerpThing(float):
    """A descriptor class for LerpThing.

    If an attribute could either be a constant value, or a LerpThing, use this
    descriptor to automatically handle this.

    Note
    ----
    This is a proof of concept.  This might or might not stay in here, the
    interface might or might not change.  I'm not sure if this has any
    advantages over a property, except not having so much boilerplate in your
    class if you have multiple LerpThings in it.

    Note 2
    ----
    In contrast to a normal LerpThing, you access the `AutoLerpThing`
    like a normal attribute, not like a method call.

    Use it like this:

        class Asteroid:
            angle = AutoLerpThing()

            def __init__(self):
                self.angle = (0, 360, 10)  # Will do one full rotation over 10 seconds

        asteroid = Asteroid()
        asteroid.angle
            --> 107.43224363999998
        asteroid.angle
            --> 129.791468736

    """
    def __set_name__(self, obj: object, name: str) -> None:
        self.attrib = f'__lerpthing_{name}'

    def __set__(self, obj: float, val: float) -> None:
        if isinstance(val, (int, float)):
            obj.__setattr__(self.attrib, val)
        elif isinstance(val, LerpThing):
            obj.__setattr__(self.attrib, val)
        elif isinstance(val, (tuple, list, set)):
            obj.__setattr__(self.attrib, LerpThing(*val))
        else:
            raise TypeError(f'{self.attrib} must be either a number or a LerpThing')

    def __get__(self, obj: float, objtype: Type[float]) -> Self | None | float:
        if obj is None:
            return self

        val = obj.__getattribute__(self.attrib)
        return val() if isinstance(val, LerpThing) else val


@dataclass(order=True)
class Cronjob:
    """Input data for the `CronD` class

    There is no need to instantiate this class yourself, `CronD.add` gets 3
    parameters.

    Parameters
    ----------
    cooldown: Cooldown | float
        Cooldown in seconds before the task runs
    task: callable
        A zero parameter callback
        If you want to provide parameters to the called function, either
        provide a wrapper to it, or use a `functools.partial`.
    repeat: False
        Description of .

    """
    cooldown: Cooldown | float
    task: Callable = field(compare=False)
    repeat: bool = field(compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.cooldown, Cooldown):
            self.cooldown = Cooldown(self.cooldown)


class CronD:
    """A job manager class.
A job manager class named after the unix scheduling daemon.
A job manager class named after the unix scheduling daemon.

    In the spirit of unix's crond, this class can be used to run functions
    after a cooldown once or repeatedly.

        crond = CronD()

        # `run_after_ten_seconds()` will be run after 10s.
        cid = crond.add(10, run_after_ten_seconds, False)

        # Remove the job with the id `cid` if it has not yet run or repeats.
        crond.remove(cid)


    Parameters
    ----------

    Attributes
    ----------
    heap: list[Cronjob]

    """
    def __init__(self) -> None:
        self.heap = []

    def add(self, cooldown: Cooldown, task: Callable, repeat: bool = False) -> ReferenceType[Cronjob]:
        """Schedule a new task.

        Parameters
        ----------
        cooldown: Cooldown | float
            Time to wait before running the task

        task: callable
            A zero parameter callback function

        repeat: bool = False
            If `True`, job will repeat infinitely or until removed.

        Returns
        -------
        cid: weakref.ref
            cronjob id.  Use this to remove a pending or repeating job.

        """
        cj = Cronjob(cooldown, task, repeat)
        heapq.heappush(self.heap, cj)
        return weakref.ref(cj)

    def remove(self, cid: ReferenceType[Cronjob]) -> None:
        """Remove a pending or repeating job.

        Does nothing if the job is already finished.

        Parameters
        ----------
        cid: weakref.ref
            Cronjob ID

        Returns
        -------
        None

        """
        if cid is not None:
            self.heap.remove(cid())

    def update(self) -> None:
        """Run all jobs that are ready to run.

        Will reschedule jobs that have `repeat = True` set.

        Returns
        -------
        None

        """
        while self.heap and self.heap[0].cooldown.cold():
            cronjob = heapq.heappop(self.heap)
            cronjob.task()
            if cronjob.repeat:
                cronjob.cooldown.reset(wrap=True)
                heapq.heappush(self.heap, cronjob)
