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
import time
import weakref

from dataclasses import dataclass, field, InitVar


class Cooldown:
    """A cooldown/counter class to wait for stuff in games.

        cooldown = Cooldown(5)

        while True:
            do_stuff()

            if key_pressed
                if key == 'P':
                    cooldown.pause()
                elif key == 'ESC':
                    cooldown.start()

            if cooldown.cold():
                launch_stuff()
                cooldown.reset()

    This can be used to time sprite animation frame changes, weapon cooldown in
    shmups, all sorts of events when programming a game.

    If you want to use the cooldown more as a timing gauge, e.g. to modify
    acceleration of a sprite over time, have a look at the `LerpThing` class
    below, which makes this incredibly easy.

    Once instantiated, it saves the current time as t0.  On every check, it
    compares the then current time with t0 and returns as 'cold' if the
    cooldown time has passed.

    The cooldown can be paused, in which case it saves the time left.  On
    restart, it'll set again t0 to the remaining time and continues to compare
    as normal against the left cooldown time.

    At any time, the cooldown can be reset to its initial or a new value.

    A cooldown can be compared to int/float/bool, in which case the `remaining`
    property is used.

    Cooldown provides a "copy constructor", meaning you can initialize a new
    cooldown with an existing one.  In contrast to the compare operations,
    which work on the time remaining, this uses the `duration` attribute.

    Note, that only the duration is used.  The pause state is *not*.

    In case you want to initialize one `Cooldown` with another, the `duration`
    attribute is used.

    Parameters
    ----------
    duration: float | pgcooldown.Cooldown
        Time to cooldown in seconds

    cold: bool = False
        Start the cooldown already cold, e.g. for initial events.

    Attributes
    ----------
    remaining: float
        remaining "temperature" to cool down from

    duration: float
        When calling `reset`, the cooldown is set to this value.
        Can be modified directly or by calling `cooldown.reset(duration)`

    normalized: float
        Give the remaining time as fraction between 0 and 1.

    paused: bool
        to check if the cooldown is paused.

    cold: bool
        Has the time of the cooldown run out?

    hot: bool
        Is there stil time remaining before cooldown?  This is just for
        convenience to not write `cooldown not cold` all over the place.

    """
    def __init__(self, duration, cold=False, paused=False):
        if isinstance(duration, Cooldown):
            self.duration = duration.duration
        else:
            self.duration = float(duration)
        self.t0 = time.time()
        self.paused = paused
        self._remaining = duration if paused else 0
        self.set_cold(cold)

    def __call__(self):
        return self.remaining()

    def __repr__(self):
        return f'Cooldown(duration={self.duration}, cold={self.cold()}, paused={self.paused})'

    def __hash__(self): id(self)  # noqa: E704
    def __bool__(self): return self.hot()  # noqa: E704
    def __int__(self): return int(self.temperature())  # noqa: E704
    def __float__(self): return float(self.temperature())  # noqa: E704
    def __lt__(self, other): return float(self) < other  # noqa: E704
    def __le__(self, other): return float(self) <= other  # noqa: E704
    def __eq__(self, other): return float(self) == other  # noqa: E704
    def __ne__(self, other): return float(self) != other  # noqa: E704
    def __gt__(self, other): return float(self) > other  # noqa: E704
    def __ge__(self, other): return float(self) >= other  # noqa: E704

    def reset(self, new=0, wrap=False):
        """reset the cooldown, optionally pass a new temperature.

        To reuse the cooldown, it can be reset at any time, optionally with a
        new duration.

        reset() also clears pause.

        Parameters
        ----------
        new: float = 0
            If not 0, set a new timeout value for the cooldown

        wrap: bool = False
            If `wrap` is `True` and the cooldown is cold, take the time
            overflown into account:

            e.g. the temperature of a Cooldown(10) after 12 seconds is `-2`.

                `cooldown.reset()` will set it back to 10.
                `cooldown.reset(wrap=True)` will set it to 8.

            Use `wrap=False` if you need a constant cooldown time.
            Use `wrap=True` if you have a global heartbeat.

            If the cooldown is still hot, `wrap` is ignored.

        Returns
        -------
        self
            Can be e.g. chained with `pause()`

        """

        if new:
            self.duration = new

        overflow = (0 if self.hot() or not wrap or self.duration == 0
                    else -self.temperature() % self.duration)
        self.t0 = time.time() - overflow

        self.paused = False

        return self

    def cold(self):
        """Current state of the cooldown.

        The cooldown is cold, if all its time has passed.  From here, you can
        either act on it and/or reset.

        Returns
        -------
        bool
            True if cold

        Note
        ----
        Since v0.2.8, this is no longer a property but a function.

        """
        return self.temperature() <= 0

    def set_cold(self, state):
        """Immediately set the remaining time to zero.

        `duration` is not impacted by this.  After a `reset()` the cooldown
        will behave as before.
        """

        if state:
            self.t0 = time.time() - self.duration

    def hot(self):
        """Counterpart to cold() if you prefere this more."""
        return self.temperature() > 0

    def temperature(self):
        """The time difference to the cooldown duration.

        `temperature` gives the time difference between now start/reset of the
        `Cooldown`.  Can be below 0 once the `Cooldown` is cold.
        Also see `remaining()`

        Note
        ----
        Since v0.2.8, this is no longer a property but a function.
        """
        if self.paused:
            return self._remaining
        else:
            return self.duration - (time.time() - self.t0)

    def set_to(self, t=0):
        """Set the current remaining time to `t`.

        Raises
        ------
        ValueError
            Setting it to a value greater than the current `duration` will
            raise raise an exception.  Use `reset(new_duration) instead.
        """
        if self.paused:
            if t:
                self._remaining = t
        else:
            if t > self.duration:
                raise ValueError('Cannot set remaining time greater than duration.  Use reset() instead')

            self.t0 = time.time() - self.duration + t

    def remaining(self):
        """Same as temperature, but doesn't go below 0.

        `remaining` gives exactly that, the time remaining in the cooldown.  If
        the `Cooldown` is cold, it always reports 0.

        Raises
        ------
        ValueError
            Setting it to a value greater than the current `duration` will
            raise raise an exception.  Use `reset(new_duration) instead.

        Note
        ----
        Since v0.2.8, this is no longer a property but a function.

        """
        return max(self.temperature(), 0)

    def normalized(self):
        """Return the time left as fraction between 0 and 1.

        Use this as `t` for lerping or easing.

        Note
        ----
        Since v0.2.8, this is no longer a property but a function.

        """
        return (1 - self.remaining() / self.duration) if self.duration else 0

    def pause(self):
        """Pause the cooldown.

        This function can be chained to directly pause from the constructor:

            cooldown.pause()
            cooldown = Cooldown(60).pause()

        Returns
        -------
        self
            For chaining.

        """

        self._remaining = self.remaining()
        self.paused = True

        return self

    def start(self):
        """Restart a paused cooldown."""
        if not self.paused: return self

        self.paused = False
        self.set_to(self._remaining)
        self._remaining = 0

        return self


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
        Values at t == 0 and t == 1

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

    """
    vt0: float
    vt1: float
    duration: InitVar[Cooldown | float]
    ease: callable = lambda x: x
    repeat: int = 0

    def __post_init__(self, duration):
        self.duration = duration if isinstance(duration, Cooldown) else Cooldown(duration)

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

    def __call__(self):
        """Return the current lerped value"""
        # Note: Using cold precalculated instead of calling it twice, gave a
        # 30% speed increase!
        cold = self.duration.cold()
        if cold and self.repeat:
            if self.repeat == 2:
                self.vt0, self.vt1 = self.vt1, self.vt0
            self.duration.reset(wrap=True)
            cold = False

        if not cold:
            return (self.vt1 - self.vt0) * self.ease(self.duration.normalized()) + self.vt0

        return self.vt1

    def __hash__(self): id(self)  # noqa: E704
    def __bool__(self): return bool(self())  # noqa: E704
    def __int__(self): return int(self())  # noqa: E704
    def __float__(self): return float(self())  # noqa: E704
    def __lt__(self, other): return self() < other  # noqa: E704
    def __le__(self, other): return self() <= other  # noqa: E704
    def __eq__(self, other): return self() == other  # noqa: E704
    def __ne__(self, other): return self() != other  # noqa: E704
    def __gt__(self, other): return self() > other  # noqa: E704
    def __ge__(self, other): return self() >= other  # noqa: E704

    def finished(self):
        """Just a conveninence wrapper for self.interval.cold"""
        return self.duration.cold()


class AutoLerpThing:
    """A descriptor class for LerpThing.

    If an attribute could either be a constant value, or a LerpThing, use this
    descriptor to automatically handle this.

    Note
    ----
    This is a proof of concept.  This might or might not stay in here, the
    interface might or might not change.  I'm not sure if this has any
    advantages over a property, except not having so much boilerplate in your
    class if you have multiple LerpThings in it.

    Use it like this:
        class SomeClass:

            usage1 = AutoLerpThing()
            usage2 = AutoLerpThing()
            usage3 = AutoLerpThing()

            def __init__(self):
                self.usage1 = 7
                self.usage2 = (0, 360, 5)
                self.usage3 = LerpThing(0, 360, 5)

        x = SomeClass()
        print(x.lerp)
        sleep(duration / 2)
        print(x.lerp)

    """
    def __set_name__(self, obj, name):
        self.attrib = f'__lerpthing_{name}'

    def __set__(self, obj, val):
        if isinstance(val, (int, float)):
            obj.__setattr__(self.attrib, val)
        elif isinstance(val, LerpThing):
            obj.__setattr__(self.attrib, val)
        elif isinstance(val, (tuple, list, set)):
            obj.__setattr__(self.attrib, LerpThing(*val))
        else:
            raise TypeError(f'{self.attrib} must be either a number or a LerpThing')

    def __get__(self, obj, parent):
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
    task: callable = field(compare=False)
    repeat: False = field(compare=False)

    def __post_init__(self):
        if not isinstance(self.cooldown, Cooldown):
            self.cooldown = Cooldown(self.cooldown)


class CronD:
    """A job manager class.

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
    def __init__(self):
        self.heap = []

    def add(self, cooldown, task, repeat=False):
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

    def remove(self, cid):
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

    def update(self):
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
