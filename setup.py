import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

NAME = 'pgn2gif'
AUTHOR = 'Deniz Kizilirmak'
URL = 'https://github.com/dn1z/pgn2gif'
DESCRIPTION = 'A small tool that generates gif of chess game'

VERSION = '1.2'

REQUIRES_PYTHON = '>=3.5'
REQUIRED = ['pillow']

here = os.path.dirname(__file__)
try:
    with open(os.path.join(here, 'README.md')) as f:
        LONG_DESCRIPTION = f.read()
except:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name=NAME,
    author=AUTHOR,
    url=URL,
    license='MIT',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    package_data={
        'pgn2gif': ['assets/*.png']
    },
    packages=['pgn2gif'],
    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    entry_points={
        'console_scripts': ['pgn2gif = pgn2gif:main']
    },
)
