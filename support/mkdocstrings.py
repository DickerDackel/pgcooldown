#!/bin/env python3

from os.path import isdir


DOCSTRINGS = {
    'MODULE': """Cooldown & co...

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

Since LerpThing obviously needs lerp functions internally, the 3 convenience
functions `lerp`, `invlerp`, and `remap` are provided.

Finally, the need to use Cooldown for scheduling the creations of game
objects, the CronD class was added.  It schedules functions to run after a
wait period.

Note, that CronD doesn't do any magic background timer stuff, it needs to be
updated in the game loop.

    crond = CronD()
    crond.add(1, lambda: create_enemy(screen.center))
    crond.add(2, lambda: create_enemy(screen.center))
    crond.add(3, lambda: create_enemy(screen.center))
    crond.add(4, lambda: create_enemy(screen.center))

    while True:
        ...
        crond.update()

""",

    'LERP': """lerp, invlerp and remap
Exported for convenience, since these are internally used in the LerpThing.

These are your normal lerp functions.

    lerp(a: float, b:float, t) -> float
        Returns interpolation from a to b at point in time t

    invlerp(a: float, b: float, v: float) -> float
        Returns t for interpolation from a to b at point v.

    remap(a0: float, b0: float, a1: float, b1: float, v0: float) -> float
        Maps point v0 in range a0/b0 onto range a1/b1.

Example function or class method with PEP 484 type annotations.
with the NumPy docstring style.

Note: Don't include the  parameter.

Parameters
----------
param1
    The first parameter.
param2
    The second parameter.

Returns
-------
bool
    True if successful, False otherwise.

Raises
------
Exception
    True if successful, False otherwise.

""",

    'COOLDOWN': """A cooldown/counter class to wait for stuff in games.

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

This can be used to time sprite animation frame changes, weapon
cooldown in shmups, all sorts of events when programming a game.

If you want to use the cooldown more as a timing gauge, e.g. to modify
acceleration of a sprite over time, have a look at the `LerpThing`
class below, which makes this incredibly easy.

Once instantiated, it saves the current time as t0.  On every check,
it compares the then current time with t0 and returns as 'cold' if the
cooldown time has passed.

The cooldown can be paused, in which case it saves the time left.  On
restart, it'll set again t0 to the remaining time and continues to
compare as normal against the left cooldown time.

At any time, the cooldown can be reset to its initial or a new value.

A cooldown can be compared to int/float/bool, in which case the
`remaining` property is used.

Cooldown provides a "copy constructor", meaning you can initialize a
new cooldown with an existing one.  The full state of the initial
cooldown is used, including `paused`, `wrap`, and the remaining time.

Depending on the wrap setting, when reset, the cooldown is either
reset to the initial duration, or the time that has passed since the
cooldown ended is substracted.  E.g.

    c = Cooldown(1, wrap=True)
    sleep(1.5)
    c.reset()

        --> c.remaining is now 0.5, not 1

Cooldown instances can be used as an iterator, returning the time
remaining.


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


Attributes
----------
All attributes are read/write.

duration: float
    When calling `reset`, the cooldown is set to this value. Can be
    assigned to directly or by calling `cooldown.reset(duration)`

temperature: float
    The time left (or passed) until cooldown.  Will go negative once
    the cooldown time has passed.

remaining: float
    Same as temperature, but will not go below 0.  When assigning, a
    negative value will be reset to 0.

normalized: float
    returns the current "distance" in the cooldown between 0 and 1,
    with one being cold.

paused: bool
    to check if the cooldown is paused.  Alternatively use
    cooldown.pause()/.start()/.is_paused() if you prefer methods.

wrap: bool
    Activate or deactivate wrap mode.


Methods
-------
Cooldown provides a __repr__, the comparism methods <, <=, ==, >=, >
and can be converted to float, int, and bool.  The 'temperature' value
is used for this, so results can be negative.

cold(): bool
    Has the time of the cooldown run out?

hot(): bool
    Is there stil time remaining before cooldown?  This is just for
    convenience to not write `cooldown not cold` all over the place.

reset([new-duration]):
    Resets the cooldown.  Without argument, resets to the current
    duration, otherwise the given value.  See wrap for nuance.

pause(), start(), is_paused():
    Pause, start, check the cooldown.  Time is frozen during the
    pause.

set_to(val):
    Deprecated, assign to cooldown.duration instead.

set_cold():
    Deprecated, assign to cooldown.duration instead.

""",

    'COOLDOWN_RESET': """reset the cooldown, optionally pass a new temperature.

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

""",

    'COOLDOWN_COLD': """Current state of the cooldown.

The cooldown is cold, if all its time has passed.  From here, you can
either act on it and/or reset.

Returns
-------
bool
    True if cold

Note
----
Since v0.2.8, this is no longer a property but a function.

""",

    'COOLDOWN_HOT': """Counterpart to cold() if you prefere this more.
""",

    'COOLDOWN_PAUSE': """Pause, start, check status of the cooldown.

    cooldown.pause()
    if cooldown.is_paused():
        ...
    cooldown.start()

Returns
-------
self
    For chaining.

""",
    'COOLDOWN_SET_COLD': """Force the cooldown to cold.

This does basically the same as setting the `temperature` property to zero.

Returns
-------
None

Note
----
This was changed from a property to a function in v0.2.8, due to the
performance impact of properties.  With the rewrite in C,this is no longer an
issue.

If you prefer writing to an attribute insteadof calling a setter, use
`temperature` or `remaining`.
""",
    'COOLDOWN_SET_TO': """Set the remaining time until cold

This does basically the same as assigning to `temperature` or `remaining`.

Returns
-------
None

Note
----
This was changed from a property to a function in v0.2.8, due to the
performance impact of properties.  With the rewrite in C,this is no longer an
issue.

If you prefer writing to an attribute insteadof calling a setter, use
`temperature` or `remaining`.
""",

    'COOLDOWN_DURATION': """duration: float
    When calling `reset`, the cooldown is set to this value. Can be
    assigned to directly or by calling `cooldown.reset(duration)`
""",
    'COOLDOWN_WRAP': """wrap: bool
    Activate or deactivate wrap mode.
""",
    'COOLDOWN_PAUSED': """paused: bool
    to check if the cooldown is paused.  Alternatively use
    cooldown.pause()/.start()/.is_paused() if you prefer methods.
""",
    'COOLDOWN_TEMPERATURE': """temperature: float
    The time left (or passed) until cooldown.  Will go negative once
    the cooldown time has passed.
""",
    'COOLDOWN_REMAINING': """remaining: float
    Same as temperature, but will not go below 0.  When assigning, a
    negative value will be reset to 0.
""",
    'COOLDOWN_NORMALIZED': """normalized: float
    returns the current "distance" in the cooldown between 0 and 1,
    with one being cold.
""",
}

if not isdir('include'):
    print('Must be used in top of project directory')
    raise SystemExit

with open('include/docstrings.h', 'w') as f:
    for name, docstring in DOCSTRINGS.items():
        ds = '\\n'.join(docstring.replace('"', '\\"').splitlines())
        print(f'#define DOCSTRING_{name} "{ds}"', file=f)
