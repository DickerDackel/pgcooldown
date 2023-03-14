import time


class DeltaTime:
    """A class to keep track of time between calls.

        delta_time = DeltaTime()
        print(dt.dt)
        sleep(1)
        print(dt.dt)

    Pygame comes with its own time tracking function in pygame.time, but
    Cooldown and DeltaTime are still useful enough for other frameworks like
    pyglet, so we're tracking time outself.
    """

    def __init__(self):
        self.prev = time.time()

    @property
    def dt(self):
        now = time.time()
        dt = now - self.prev
        self.prev = now
        return dt


class Cooldown:
    """A cooldown class, counting down to zero, optionally repeating.

        cooldown = Cooldown(5)

    Parameters:

        temperature: float - "temperature" to cool down from
        init: float - default to initialize the cooldown after each reset()
        disabled: bool = False - to temporarily disable the cooldown

    Synopsis:

        clock = pygame.time.Clock()
        cooldown = Cooldown(5)

        while True:
            dt = clock.get_time() / 1000.0

            ...
            cooldown(delta_time)
            if cooldown.cold:
                # do stuff
                # Reset the timer to wait again
                cooldown.reset()

            ...

    """

    def __init__(self, init, disabled=False):
        self.temperature = self.init = init
        self.disabled = False

    def __call__(self, dt):
        """cooldown(dt) -> float

        reduces and returns the cooldown.

        Use this, if delta time is handled by the main loop.  If you don't want
        to calculate and take care of delta time, use the iterator versin
        instead.
        """
        if self.disabled or self.temperature == 0:
            return self.temperature

        self.temperature -= dt
        if self.temperature < 0:
            self.temperature = 0

        return self.temperature

    def __iter__(self):
        """cooldown = Cooldown(1.5)
        while True:
            if next(cooldown): return

            # do shit...
            cooldown.reset()

        Basically the same as __call__, but time is tracked inside and not
        passed from the main game loop.
        """

        dt = DeltaTime()
        while True:
            if self.disabled or self.temperature == 0:
                return self.temperature

            yield self(dt.dt)

    def reset(self):
        """cooldown.reset()

        reset the cooldown to its initial temperature to use it again
        """
        self.temperature = self.init

    @property
    def cold(self):
        """if cooldown.cold: ...

        the cooldown is cold, if it is down to zero.  From here, you can either
        act on it and/or reset.
        """

        return self.temperature <= 0
