###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

from setuptools import setup

setup(
    name='yinsolidated',
    version='1.1.1',
    description='Parses the consolidated YIN model format',
    py_modules=['yinsolidated'],
    install_requires=[
        'lxml >= 3.7.3',
        'xpathparser >= 1.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='MIT'
)
