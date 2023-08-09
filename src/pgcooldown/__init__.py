import time

from dataclasses import dataclass, InitVar


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

            if cooldown.cold:
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
    def __init__(self, duration, cold=False):
        if isinstance(duration, Cooldown):
            self.duration = duration.duration
        else:
            self.duration = float(duration)
        self.t0 = time.time()
        self.paused = False
        self._remaining = 0
        self.cold = cold

    def __hash__(self): id(self)  # noqa: E704
    def __bool__(self): return self.hot  # noqa: E704
    def __int__(self): return int(self.temperature)  # noqa: E704
    def __float__(self): return float(self.temperature)  # noqa: E704
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

        overflow = (0 if self.hot or not wrap
                    else -self.temperature % self.duration)
        self.t0 = time.time() - overflow

        self.paused = False

        return self

    @property
    def cold(self):
        """Current state of the cooldown.

        The cooldown is cold, if all its time has passed.  From here, you can
        either act on it and/or reset.

        Can be set to true to immediately set the timer to zero.  `duration`
        after reset is not impacted by this.

        Returns
        -------
        bool
            True if cold

        """
        return self.remaining <= 0

    @cold.setter
    def cold(self, state):
        if state:
            self.t0 = time.time() - self.duration

    @property
    def hot(self):
        """`not cooldown.cold` (See above)"""
        return not self.cold

    @property
    def temperature(self):
        """The time difference to the cooldown duration.

        `temperature` gives the time difference between now start/reset of the
        `Cooldown`.  Can be below 0 once the `Cooldown` is cold.

        Can also be set.

        Raises
        ------
        ValueError
            Setting it to a value greater than the current `duration` will
            raise raise an exception.  Use `reset(new_duration) instead.

        """
        if self.paused:
            return self._remaining
        else:
            return self.duration - (time.time() - self.t0)

    @temperature.setter
    def temperature(self, t=0):
        if self.paused:
            if t:
                self._remaining = t
        else:
            if t > self.duration:
                raise ValueError('Cannot set remaining time greater than duration.  Use reset() instead')

            self.t0 = time.time() - self.duration + t

    @property
    def remaining(self):
        """Same as temperature, but doesn't go below 0.

        `remaining` gives exactly that, the time remaining in the cooldown.  If
        the `Cooldown` is cold, it always reports 0.

        Can also be set.

        Raises
        ------
        ValueError
            Setting it to a value greater than the current `duration` will
            raise raise an exception.  Use `reset(new_duration) instead.

        """
        return max(self.temperature, 0)

    @remaining.setter
    def remaining(self, t=0):
        self.temperature = t

    @property
    def normalized(self):
        """Return the time left as fraction between 0 and 1.

        Use this as `t` for lerping or easing.

        """
        return 1 - self.remaining / self.duration

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

        self._remaining = self.remaining
        self.paused = True

        return self

    def start(self):
        """Restart a paused cooldown."""
        if not self.paused: return self

        self.paused = False
        self.remaining = self._remaining
        self._remaining = 0

        return self


@dataclass
class LerpThing:
    """A time based generic gauge that lerps between 2 points.

    This class can be used for scaling, color shifts, momentum, ...

    It gets initialized with 2 Values for t0 and t1, and a time `interval`,
    then it lerps between these values.

    Once the time runs out, the lerp can stop, repeat from start or bounce back
    and forth.

    An optional easing function can be put on top of `t`.

    Parameters
    ----------
    vt0,
    vt1: [int | float]
        Values at t == 0 and t == 1

    interval: Cooldown The length of the lerp.  This length of the interval is
    mapped onto the range 0 - 1 as `t`.

    ease: callable = lambda x: x
        An optional easing function to put over t

    repeat: int = 0
        After the interval has finished, how to proceed?

            0: Don't repeat, just stop transmogrifying
            1: Reset and repeat from start
            2: Bounce back and forth.  Note, that bounce back is implemented by
               swapping vt0 and vt1.

    Attributes
    ----------
    v: float
        The lerped value.  This is a property which dynamically lerps the
        value.

    """
    vt0: float
    vt1: float
    interval: InitVar[Cooldown | float]
    ease: callable = lambda x: x
    repeat: int = 0

    def __post_init__(self, interval):
        self.interval = interval if isinstance(interval, Cooldown) else Cooldown(interval)

    def __call__(self):
        return self.v

    @property
    def v(self):
        """Get the current value of the LerpThing."""

        lerp = lambda a, b, t: t * (b - a) + a

        if self.interval.cold and self.repeat:
            if self.repeat == 2:
                self.vt0, self.vt1 = self.vt1, self.vt0
            self.interval.reset(wrap=True)

        if self.interval.hot:
            t = self.interval.normalized
            return lerp(self.vt0, self.vt1, self.ease(t))

        return self.vt1
