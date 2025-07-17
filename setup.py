from setuptools import Extension, setup

setup(
    include_package_data=True,
    package_data={'pgcooldown': ['py.typed']},
    ext_package = 'pgcooldown',
    ext_modules=[
        Extension('_pgcooldown', ['src_c/pgcooldown.c'], include_dirs=["include"]),
    ]
)
