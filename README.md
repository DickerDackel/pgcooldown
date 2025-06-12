# pgcooldown - Cooldown & co...

## DESCRIPTION

This module started with just the Cooldown class, which can be used check if a
specified time has passed.  It is mostly indended to be used to control
objects in a game loop, but it is general enough for other purposes as well.

```python
fire_cooldown = Cooldown(1, cold=True)
while True:
    if fire_shot and fire_cooldown.cold():
        fire_cooldown.reset()
        launch_bullet()

    ...
```

With the usage of Cooldown on ramp data (e.g. a Lerp between an opaque and a
fully transparent sprite over the time of n seconds), I came up with the
LerpThing.  The LerpThing gives you exactly that.  A lerp between `from` and
`to` mapped onto a `duration`.

```python
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

```python
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
