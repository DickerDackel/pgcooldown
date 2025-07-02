#!/bin/env python3

from os.path import isdir


DOCSTRINGS = {
    'LERP': """lerp, invlerp and remap
Exported for convenience, since these are internally used in the LerpThing.

These are your normal lerp functions.

    lerp(a: float, b:float, t) -> float
        Returns interpolation from a to b at point in time t

    invlerp(a: float, b: float, v: float) -> float
        Returns t for interpolation from a to b at point v.

    remap(a0: float, b0: float, a1: float, b1: float, v0: float) -> float
        Maps point v0 in range a0/b0 onto range a1/b1.

"point in time" in this context means between 0 and 1.

    lerp(0, 10, 0.5) --> 5
    invlerp(0, 10, 5) --> 0.5
    remap(0, 10, 0, 100, 5) --> 50

""",

    'COOLDOWN': """Track a cooldown over a period of time.

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

Cooldown can be used to time sprite animation frame changes,
weapon cooldown in shmups, all sorts of events when programming a
game.

If you want to use the cooldown more as a timing gauge, e.g. to
modify acceleration of a sprite over time, have a look at the
`LerpThing` class in this package, which makes this incredibly
easy.

When instantiated (and started), Cooldown stores the current time.
The cooldown will become `cold` when the given duration has passed.

While a cooldown is paused, the remaining time doesn't change.

At any time, the cooldown can be reset to its initial or a new
value.

A cooldown can be compared to int/float/bool, in which case the
`remaining` property is used.

Cooldown provides a "copy constructor", meaning you can
initialize a new cooldown with an existing one.  The full state
of the initial cooldown is used, including `paused`, `wrap`, and
the remaining time.

When a cooldown is reset, depending on when you checked the
`cold` state, more time may have passed than the actual cooldown
duration.

The `wrap` attribute decides, if the cooldown then is just reset
back to the duration, or if this additional time is taken into
account.  The `wrap` argument of the `reset` function overwrites
the default configuration of the cooldown instance.

    c0 = Cooldown(5)
    c1 = Cooldown(5, wrap=True)
    sleep(7)
    c0.temperature, c1.temperature
        --> -2.000088164 -2.0000879129999998

    c0.reset()
    c1.reset()
    c0.temperature, c1.temperature
        --> 4.999999539 2.999883194

    sleep(7)
    c0.temperature, c1.temperature
        --> -2.000189442 -4.000306759000001

    c0.reset(wrap=True)
    c1.reset(wrap=False)
    c0.temperature, c1.temperature
        --> 2.999748423 4.999999169

A cooldown can be used as an iterator, returning the time
remaining.

    for t in Cooldown(5):
        print(t)
        sleep(1)

    4.998921067
    3.998788201
    2.998640238
    1.9984825379999993
    0.998318566


Arguments
---------
duration: float | pgcooldown.Cooldown
    Time to cooldown in seconds

cold: bool = False
    Start the cooldown already cold, e.g. for initial events.

paused: bool = False
    Created the cooldown in paused state.  Use `cooldown.start()` to
    run it.

wrap: bool = False
    Set the reset mode to wrapped (see above).
    Can be overwritten by the `wrap` argument to the `reset` function.


Attributes
----------
All attributes are read/write.

duration: float
    When calling `reset`, the cooldown is set to this value. Can be
    assigned to directly or by calling `cooldown.reset(duration)`

temperature: float
    The time left (or passed) until cooldown.  Will go negative once the
    cooldown time has passed.

remaining: float
    Same as temperature, but will not go below 0.  When assigning, a
    negative value will be reset to 0.

normalized: float
    returns the current "distance" in the cooldown between 0 and 1, with
    one being cold.  Ideal for being used in an easing function or lerp.

paused: bool
    to check if the cooldown is paused.  Alternatively use
    cooldown.pause()/.start()/.is_paused() if you prefer methods.

wrap: bool
    Activate or deactivate wrap mode.


Methods
-------
Cooldown provides a __repr__, the comparism methods <, <=, ==, >=, >,
can be converted to float/int/bool, and can be used as an iterator.  The
'temperature' value is used for all operations, so results can be
negative.  As an iterator, StopIteration is raised when the temperature
goes below 0 though.

cold(): bool
    Has the time of the cooldown run out?

hot(): bool
    Is there stil time remaining before cooldown?  This is just for
    convenience to not write `not cooldown.cold()` all over the place.

reset([new-duration], *, wrap=bool):
    Resets the cooldown.  Without argument, resets to the current
    duration, otherwise the given value.  See wrap for nuance.

    `reset()` return `self`, so it can e.g. be chained with `pause()`


pause(), start(), is_paused():
    Pause, start, check the cooldown.  Time is frozen during the
    pause.

set_to(val):
    Same as `cooldown.temperature = val`.

set_cold():
    Same as `cooldown.temperature = 0`.

""",
}

if not isdir('include'):
    print('Must be used in top of project directory')
    raise SystemExit

with open('include/docstrings.h', 'w') as f:
    for name, docstring in DOCSTRINGS.items():
        ds = '\\n'.join(docstring.replace('"', '\\"').splitlines())
        print(f'#define DOCSTRING_{name} "{ds}"', file=f)
