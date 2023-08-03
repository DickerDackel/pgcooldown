import time


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

    Once instantiated, it saves the current time as t0.  On every check, it
    compares the then current time with t0 and returns as 'cold' if the
    cooldown time has passed.

    The cooldown can be paused, in which case it saves the time left.  On
    restart, it'll set again t0 to the remaining time and continues to compare
    as normal against the left cooldown time.

    At any time, the cooldown can be reset to its initial or a new value.

    A cooldown can be compared to int/float/bool, in which case the `remaining`
    property is used.

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

    def reset(self, new=0):
        """reset the cooldown, optionally pass a new temperature.

            cooldown.reset()
            cooldown.reset(new_temp)

        Parameters
        ----------
        new: float = 0
            If not 0, set a new timeout value for the cooldown

        Returns
        -------
        self
            Can be e.g. chained with `pause()`

        """
        if new:
            self.duration = new
        self.t0 = time.time()
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
    def remaining(self):
        """Time remaining until cold.

        This property is also aliased to "temperature".

            time_left = cooldown.remaining
            time_left = cooldown.temperature

        Assigning to this value will change the current stateof the cooldown
        accordingly.

        Raises
        ------
        ValueError
            Setting it to a value greater than the current `duration` will
            raise raise an exception.  Use `reset(new_duration) instead.

        """
        if self.paused:
            return self._remaining
        else:
            remaining = self.duration - (time.time() - self.t0)
            return remaining if remaining >= 0 else 0

    @remaining.setter
    def remaining(self, t=0):
        if self.paused:
            if t:
                self._remaining = t
        else:
            if t > self.duration:
                raise ValueError('Cannot set remaining time greater than duration.  Use reset() instead')

            self.t0 = time.time() - self.duration + self._remaining

    temperature = remaining

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
