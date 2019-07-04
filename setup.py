# -*- coding: utf-8 -*-
"""
Create by wang_yang1980@hotmail.com at 7/3/19
"""
import re
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


CURDIR = dirname(abspath(__file__))

CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()
with open(join(CURDIR, 'src','DatabaseLib' , 'version.py')) as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
DESCRIPTION = 'Database Library for Robot Framework based on sqlalchemy'
with open(join(CURDIR, 'requirements.txt')) as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name             = 'robotframework-databaselib',
    version          = VERSION,
    description      = DESCRIPTION,
    long_description = DESCRIPTION,
    author           = 'Wang Yang',
    author_email     = 'wang_yang1980@hotmail.com',
    url              = 'https://github.com/rainmanwy/robotframework-DatabaseLib',
    keywords         = 'robotframework testing testautomation',
    platforms        = 'any',
    classifiers      = CLASSIFIERS,
    install_requires = REQUIREMENTS,
    package_dir      = {'': 'src'},
    packages         = find_packages('src')
)