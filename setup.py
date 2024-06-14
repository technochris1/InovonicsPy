#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='inovonics',
    version='0.0.1',
    description='Inovonics serial protocol implementation',
    author='Christopher Fisk',
    author_email='technochris1@gmail.com',
    url='https://github.com/technochris1/InovonicsPy',
    packages=[
        'inovonics',
        'inovonics.protocol',
        'inovonics.comms',
    ],
    scripts=[],
    package_data={},
    install_requires=[
        'enum-compat>=0.0.2',
        'pyserial>=3.0',
    ])
