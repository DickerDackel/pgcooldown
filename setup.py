from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension('_pgcooldown', ['src_c/pgcooldown.c'],
                  include_dirs=["include"],
                  )
    ]
)
