# -*- coding: UTF-8 -*-

import setuptools
from distutils.core import setup

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='didel/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(
    name='didelcli',
    version=verstr,
    author='Baptiste Fontaine',
    author_email='b@ptistefontaine.fr',
    packages=['didel'],
    url='https://github.com/bfontaine/didelcli',
    license=open('LICENSE', 'r').read(),
    description='Didel command-line tool',
    long_description=open('README.rst', 'r').read(),
    install_requires=[
        'beautifulsoup4 >= 4.3.2',
        'lxml == 3.4.2',
        'ordereddict == 1.1',
        'requests >= 2.4.2',
    ],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts':[
            'didel = didel.cli:run'
        ]
    },
)
