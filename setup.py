#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='Tuber',
    version='0.1',

    description='Connector for various message queues',
    long_description='Connector for various message queues', #FIXME
    url='https://github.com/metno/Tuber',
    author='Lars Jørgen Solberg',
    author_email='larsjs@met.no',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['kafka-python', 'python-dateutil'],
    keywords='GTS WMO Kafka',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tuber=Tuber.Daemon:main',
        ],
    },
    test_suite = 'tests'
)
