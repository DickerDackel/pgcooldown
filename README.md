# IMPORTANT
Breaking change!  Properties gone!

I was aware, that there is a slight overhead when using properties, but
during A benchmark, that difference turned out to be 17%.

Since this package is still marked as Alpha and probably nobody is using
it besides me, the interface is now changed from properties to functions
in all places.

Tests needed to be adapted, but run clean now (and also more exact using
`pytest.approx` instead of `round`.

The following properties now need to be called as functions:

```
    cold                -> cold()
    cold.setter         -> set_cold(bool)
    hot                 -> hot()
    temperature         -> temperature()
    temperature.setter  -> set_to(val)
    remaining           -> remaining()
    remaining.setter    -> set_to(val)
    normalized          -> normalized()
    v                   -> removed, just use instance()
```

As stated initially, this is 17% less overhead when testing for cold,
etc.  Performance of LerpThing increased from 1.3mio calls to 1.8mio due
to this change.

Sorry for any inconvenience, if anybody is using this, but that bad
design decision needed to be fixed before any more people would use this.

---

# pgcooldown

Cooldown & co...

This module started with just the Cooldown class, which can be used check if a
specified time has passed.  It is mostly indended to be used to control
objects in a game loop, but it is general enough for other purposes as well.

```py
    fire_cooldown = Cooldown(1, cold=True)
    while True:
        if fire_shot and fire_cooldown.cold:
            fire_cooldown.reset()
            launch_bullet()

        ...
```

With the usage of Cooldown on ramp data (e.g. a Lerp between an opaque and a
fully transparent sprite over the time of n seconds), I came up with the
LerpThing.  The LerpThing gives you exactly that.  A lerp between `from` and
`to` mapped onto a `duration`.

```py
    alpha = LerpThing(0, 255, 5)
    while True:
        ...
        sprite.set_alpha(alpha())
        # or sprite.set_alpha(alpha.v)

        if alpha.finished:
            sprite.kill()
```

Finally, the need to use Cooldown for scheduling the creations of game
objects, the CronD class was added.  It schedules functions to run after a
wait period.

Note, that CronD doesn't do any magic background timer stuff, it needs to be
updated in the game loop.

```py
    crond = CronD()
    crond.add(1, create_enemy(screen.center))
    crond.add(2, create_enemy(screen.center))
    crond.add(3, create_enemy(screen.center))
    crond.add(4, create_enemy(screen.center))

    while True:
        ...
        crond.update()
```

## Installation

The project home is https://github.com/dickerdackel/pgcooldown

### Installing HEAD from github directly

```
pip install git+https://github.com/dickerdackel/pgcooldown
```

### Getting it from pypi

```
pip install pgcooldown
```

### Tarball from github

Found at https://github.com/dickerdackel/pgcooldown/releases

## Licensing stuff

This lib is under the MIT license.
