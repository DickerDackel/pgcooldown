# pgcooldown

A cooldown class, checking the delta time between start and now.

    cooldown = Cooldown(5)

A trigger class to wait for n seconds.

If started, it saves the current time as t0.  On every check, it compares
the then current time with t0 and returns as 'cold' if the cooldown time
has passed.

The cooldown can be paused, in which case it saves the time left.  On
restart, it'll set again t0 to the remaining time and continues to compare
as normal against the left cooldown time.

At any time, the cooldown can be reset to its initial or a new value.

Parameters:

    duration: float - Seconds to cool down

Attributes:

    remaining: float        - "temperature" to cool down from
    duration: float         - default to initialize the cooldown after each reset()
    normalized: float       - property that maps remaining into an interval between 0 and 1
    paused: bool = False    - to temporarily disable the cooldown
    hot: bool               - there is stil time remaining before cooldown
    cold: bool              - time of the cooldown has run out

Methods:

    reset()
    reset(new_cooldown_time)

	set t0 to now, remove pause state, optionally set duration to new
	value

    start()

	Start the cooldown again after a pause.

	The cooldown is started at creation time, but can be immediately
	paused by chaining.  See pause below.

    pause()

	remember time left, stop comparing delta time.  This can also be
	used to create an cooldown that's not yet running by chaining to
	the constructor:

	    cooldown = Cooldown(10).pause()


Synopsis:

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

"""

## Installation

The project home is https://github.com/dickerdackel/pgcooldown

### Getting it from pypi

```
pip install pgcooldown
```

### Tarball from github

Found at https://github.com/dickerdackel/pgcooldown/releases

## Licensing stuff

This lib is under the MIT license.
