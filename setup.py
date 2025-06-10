from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension('pgcooldown_', ['src_c/pgcooldown.c'],
                  include_dirs=["include"],
                  )
    ]
)
