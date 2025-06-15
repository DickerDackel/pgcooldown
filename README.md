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

## CLASSES

### Cooldown

```python
c = Cooldown(c)
```

Track a cooldown over a period of time.

```python
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
```

Cooldown can be used to time sprite animation frame changes, weapon
cooldown in shmups, all sorts of events when programming a game.

If you want to use the cooldown more as a timing gauge, e.g. to modify
acceleration of a sprite over time, have a look at the `LerpThing` class
in this package, which makes this incredibly easy.

When instantiated (and started), Cooldown stores the current time. The
cooldown will become `cold` when the given duration has passed.

While a cooldown is paused, the remaining time doesn't change.

At any time, the cooldown can be reset to its initial or a new value.

A cooldown can be compared to int/float/bool, in which case the
`remaining` property is used.

Cooldown provides a "copy constructor", meaning you can initialize a new
cooldown with an existing one.  The full state of the initial cooldown
is used, including `paused`, `wrap`, and the remaining time.

When a cooldown is reset, depending on when you checked the `cold`
state, more time may have passed than the actual cooldown duration.

The `wrap` attribute decides, if the cooldown then is just reset back to
the duration, or if this additional time is taken into account.  The
`wrap` argument of the `reset` function overwrites the default
configuration of the cooldown instance.

```python
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
```

IMPORTANT: wrapping is meant to keep precise timing over a long period
of time, while dealing with load peaks.  If you constantly overshoot,
you won't be able to catch back up to the full cooldown time.  Your
overshoot errors will accumulate.

A cooldown can be used as an iterator, returning the time remaining.

```python
for t in Cooldown(5):
    print(t)
    sleep(1)

4.998921067
3.998788201
2.998640238
1.9984825379999993
0.998318566
```


#### Arguments

##### duration: float | pgcooldown.Cooldown

Time to cooldown in seconds

##### cold: bool = False

Start the cooldown already cold, e.g. for initial events.

##### paused: bool = False

Created the cooldown in paused state.  Use `cooldown.start()` to
run it.

##### wrap: bool = False

Set the reset mode to wrapped (see above).
Can be overwritten by the `wrap` argument to the `reset` function.


#### Attributes

All attributes are read/write.

##### duration: float

When calling `reset`, the cooldown is set to this value. Can be assigned
to directly or by calling `cooldown.reset(duration)`

##### temperature: float

The time left (or passed) until cooldown.  Will go negative once the
cooldown time has passed.

##### remaining: float

Same as temperature, but will not go below 0.  When assigning, a
negative value will be reset to 0.

##### normalized: float

returns the current "distance" in the cooldown between 0 and 1, with one
being cold.  Ideal for being used in an easing function or lerp.

##### paused: bool

to check if the cooldown is paused.  Alternatively use
cooldown.pause()/.start()/.is_paused() if you prefer methods.

##### wrap: bool

Activate or deactivate wrap mode.


#### Methods

Cooldown provides a `__repr__`, the comparism methods `<`, `<=`, `==`,
`>=`, `>`, can be converted to `float`/`int`/`bool`, and can be used as
an iterator.  The 'temperature' value is used for all operations, so
results can be negative.  As an iterator, StopIteration is raised when
the temperature goes below 0 though.

##### cold(): bool

Has the time of the cooldown run out?

##### hot(): bool

Is there stil time remaining before cooldown?  This is just for
convenience to not write `not cooldown.cold()` all over the place.

##### reset([new-duration], *, wrap=bool):

Resets the cooldown.  Without argument, resets to the current duration,
otherwise the given value.  See wrap for nuance.

`reset()` return `self`, so it can e.g. be chained with `pause()`


##### pause(), start(), is_paused():

Pause, start, check the cooldown.  Time is frozen during the pause.

##### set_to(val):

Same as `cooldown.temperature = val`.

##### set_cold():

Same as `cooldown.temperature = 0`.

### LerpThing

```python
lt = LerpThing(vt0=32, vt1=175, duration=10, repeat=2)
sleep(1)
value = lt()
```

A time based generic gauge that lerps between 2 points.

This class can be used for scaling, color shifts, momentum, ...  It gets
initialized with 2 Values for t0 and t1, and a time `duration`, then it
lerps between these values.

Once the time runs out, the lerp can stop, repeat from start or bounce
back and forth.

An optional easing function can be put on top of `t`.

#### Parameters

##### vt0, vt1: float

The endpoints of the lerp at `t == 0` and `t == 1`

##### duration: Cooldown(1)

The length of the lerp.  This duration is mapped onto the range 0 - 1 as
`t`.

This is a `Cooldown` object, so all configuration and query options
apply, if you want to modify the lerp during its runtime.

Note: If `duration` is 0, `vt0` is always returned.

##### ease: callable = lambda x: x

An optional easing function to put over t

##### repeat: int = 0

After the duration has passed, how to proceed?

`0`: Don't repeat, just stop transmogrifying
`1`: Reset and repeat from start
`2`: Bounce back and forth.  Note, that bounce back is implemented by
swapping `vt0` and `vt1`.

##### LerpThing.finished(self)

Just a conveninence wrapper for `LerpThing.duration.cold()`

### AutoLerpThing

```python
my_class_attribute = AutoLerpThing()
```

A descriptor class for LerpThing.

If an attribute in your class could either be a constant value, or a
`LerpThing`, use this descriptor to automatically handle this.

**Note:**   This is a proof of concept.  This might or might not stay in
here, the interface might or might not change.  I'm not sure if this has
any advantages over a property, except not having so much boilerplate in
your class if you have multiple `LerpThing`s in it.

**Note 2:** In contrast to a normal LerpThing, you access the
`AutoLerpThing` like a normal attribute, not like a method call.

Use it like this:

```python
class Asteroid:
    angle = AutoLerpThing()

    def __init__(self):
        self.angle = (0, 360, 10)  # Will do one full rotation over 10 seconds

asteroid = Asteroid()
asteroid.angle
    --> 107.43224363999998
asteroid.angle
    --> 129.791468736
...
```

### CronD, Cronjob

    crond = CronD()

A job manager class.

In the spirit of unix's `crond`, this class can be used to run functions
after a cooldown once or repeatedly.  See CronJob below for how and why
to use it.

#### Methods

##### CronD.update()

Check for due jobs and run them.

##### CronD.add(cooldown, task, repeat=False)

Schedule a new task.

The `cooldown` can be either a `Cooldown` object or a `float`
representing the number of seconds.

The `task` is a zero parameter callback function that is called once the
cooldown is cold.

`repeat` (bool, default is False) decides if the cooldown will reset and
the task will run on repeat, or if the job is a one shot that will be
removed.

A job id is returned, which can be e.g. used to remove a pending or
repeating job.

##### CronD.remove(id)

Remove the scheduled job with the given id.

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
