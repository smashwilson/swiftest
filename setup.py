#!/bin/env python
# Copyright 2013 Ash Wilson

from setuptools import setup

import swiftest

setup(
    name='swiftest',
    version=swiftest.VERSION,
    description='Pythonic client for OpenSwift',
    author='Ash Wilson',
    author_email='smashwilson@gmail.com',
    url='https://github.com/smashwilson/swiftest',
    packages=['swiftest'],
    install_requires='requests>=1.2.3',
    test_requires='httpretty>=0.6.3')
