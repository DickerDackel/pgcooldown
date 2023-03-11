# cooldown

A cooldown class, counting down to zero, optionally repeating.

    cooldown = Cooldown(5)

Parameters:

    temperature: float - "temperature" to cool down from
    init: float - default to initialize the cooldown after each reset()
    disabled: bool = False - to temporarily disable the cooldown

## Synopsis:

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

The dt that's usually calculated at the beginning of a pygame main loop will be
used as a factor while counting down.

See e.g. my pygame-teletype package for an example of how it is used.

## Licensing stuff

This lib is under the MIT license.
