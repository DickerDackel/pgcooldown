# v0.3.10
- Moved type hints from stub to python where possible.
- I hate pyi files!

# v0.3.9
- Another `finished` problem that was missed by the tests

# v0.3.8
- Fixed `finished()` error with looping
- fixed test error for Cooldown.duration

# v0.3.7
- Limited repeats for LerpThing

# v0.3.6
- New lib location
- Mostly fixed stubs, not 100% yet though
- Removed unused functions
- rpeasings dependency
- typos

# v0.3.5

- Fixed a race condition in LerpThing

# v0.3.3

- Changed the overshoot behaviour of wrap

# v0.3.2 - unreleased

- Port to C
- API break, fuck it, we're < 1.0
  - Some methods have been moved back to properties
- Cooldown supports the iterator protocol now

# v0.2.14
- Fixed type error when calling float(lerp_thing)

# v0.2.13
- Fix division by zero if duration == 0

# v0.2.12
- Allow duration of 0
- Operators for LerpThing
- Test updates and enhancements

# v0.2.10
- typehints

# v0.2.9
- Pause can be passed to init, useful repr
- Note in docs, that Cooldown.reset() also unpauses.
- Update README.md

# v0.2.8
Breaking change!  Properties gone!

I was aware, that there is a slight overhead when using properties, but
during A benchmark, that difference turned out to be 17%.

Since this package is still marked as Alpha and probably nobody is using
it besides me, the interface is now changed from properties to functions
in all places.

Tests needed to be adapted, but run clean now (and also more exact using
`pytest.approx` instead of `round`.

The following properties now need to be called as functions:

    cold                -> cold()
    cold.setter         -> set_cold(bool)
    hot                 -> hot()
    temperature         -> temperature()
    temperature.setter  -> set_to(val)
    remaining           -> remaining()
    remaining.setter    -> set_to(val)
    normalized          -> normalized()
    v                   -> removed, just use instance()

As stated initially, this is 17% less overhead when testing for cold,
etc.  Performance of LerpThing increased from 1.3mio calls to 1.8mio due
to this change.

Sorry for any inconvenience, if anybody is using this, but that bad
design decision needed to be fixed if any more people would use this.

# v0.2.7
- README is mostly the docstring of the main class now
- Merge branch 'main' of https://github.com/dickerdackel/pgcooldown
- Module docs added
- Forgot Updated changelog in release

# v0.2.6.1
- Forgot Updated changelog in release

# v0.2.6
- CronD added
- Cooldown has __call__ now, returns remaining
- v0.2.5.1
- fixed URL definition in pyproject.toml

# v0.2.5.1
- fixed URL definition in pyproject.toml

# v0.2.5
- Convenience wrapper LerpThing.finished
- Doc changes
- LerpThing always returns vt0 when duration is 0
- MASSIVE speedup (>50%) in LerpThing

# v0.2.4.1
- Fixing packaging mistake on pypi

# v0.2.4a
- `interval` was a shitty name.  `duration` now.

# v0.2.4
- Added LerpThing
- reset(wrap=True), remaining vs. temperature
- Fixed b0rken Cooldown.remaining setter

# v0.2.3

- Fixed b0rken Cooldown.remaining setter
- Tracking changes now

# v0.2.2

- *bump* current dev branch
- Tests + Clarified documentation of Cooldown(cooldown)
- Added basic operators and type casts.
- Reintroduced chaining
- Merge branch 'main' of https://github.com/dickerdackel/pgcooldown
- Add Install section
- Update README.md
