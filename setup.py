#!/usr/bin/env python
from setuptools import setup, find_packages



VERSION = '0.0.1'
DESCRIPTION = 'Inovonics serial protocol implementation'
LONG_DESCRIPTION = None

setup(
    name='pyinovonics',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Christopher Fisk',
    author_email='technochris1@gmail.com',
    url='https://github.com/technochris1/InovonicsPy',
    packages=find_packages(),
    #packages=[
    #    'inovonics',
    #    'inovonics.protocol',
    #    'inovonics.comms',
    #],
    scripts=[],
    package_data={},
    install_requires=[
        'enum-compat>=0.0.2',
        'pyserial>=3.0',
    ])
