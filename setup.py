#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info < (3, 3, 0):
    exit("This project requires Python >= 3.3.")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import gxf

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = open('requirements.txt').read()
test_requirements = open('requirements-test.txt').read()

setup(
    name='gxf',
    version=gxf.__version__,
    description='Gdb Extension Framework is a bunch of python code around the gdb api.',
    long_description=readme + '\n\n' + history,
    author=gxf.__author__,
    author_email=gxf.__email__,
    url='https://github.com/wapiflapi/gxf',
    license="MIT",
    zip_safe=False,
    keywords='gxf',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    packages=['gxf'],
    package_dir={'gxf': 'gxf'},
    include_package_data=True,
    install_requires=requirements,

    test_suite='tests',
    tests_require=test_requirements
)
