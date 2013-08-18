#!/bin/env python
# Copyright 2013 Ash Wilson

from setuptools import setup

import swiftest
import os

with open('requirements.txt') as f:
    required = [line for line in f.read().splitlines() if line[0] != '#' and len(line.strip()) != 0]

setup(
    name='swiftest',
    version=swiftest.VERSION,
    description='Pythonic client for OpenSwift',
    author='Ash Wilson',
    author_email='smashwilson@gmail.com',
    url='https://github.com/smashwilson/swiftest',
    packages=['swiftest'],
    install_requires=required)
