# Copyright 2019 128 Technology, Inc.

from __future__ import print_function, absolute_import, unicode_literals

import contextlib
import copy
import os
import runpy
import sys

from lxml import etree
import pyang
import pytest

from yinsolidated.plugin import plugin

YINSOLIDATED_PLUGIN_DIRECTORY = os.path.dirname(plugin.__file__)


# Use the correct type of IO buffer depending on how strings are encoded
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def pytest_addoption(parser):
    parser.addoption("--pyang-path", action="store",
                     help="path to pyang executable")


@contextlib.contextmanager
def redirect_stdout(target):
    original = sys.stdout
    sys.stdout = target
    try:
        yield
    finally:
        sys.stdout = original


@contextlib.contextmanager
def replace_argv(new_argv):
    original_argv = copy.copy(sys.argv)
    sys.argv = new_argv
    try:
        yield
    finally:
        sys.argv = original_argv


@pytest.fixture(scope='session')
def consolidated_model(request):
    test_file_dir = os.path.dirname(os.path.realpath(__file__))
    modules_dir = os.path.join(test_file_dir, 'modules')
    main_module = os.path.join(modules_dir, 'test-module.yang')
    augmenting_module = os.path.join(modules_dir, 'augmenting-module.yang')

    pyang_args = [
        '--verbose',
        '-W', 'error',
        '-f', 'yinsolidated',
        '-p', modules_dir,
    ]

    if pyang.__version__ < '1.7.2':
        pyang_args.extend(['--plugindir', YINSOLIDATED_PLUGIN_DIRECTORY])

    pyang_args.extend([main_module, augmenting_module])
    pyang_path = request.config.getoption("--pyang-path")

    stream = StringIO()
    try:
        with redirect_stdout(stream):
            with replace_argv([pyang_path] + pyang_args):
                runpy.run_path(pyang_path, run_name="__main__")
    except SystemExit as err:
        if err.code != 0:
            raise
    finally:
        # This is a hack so we can use runpy multiple types on pytest < 5.x
        pyang.plugin.plugins = []

    try:
        yield etree.fromstring(stream.getvalue().encode())
    except etree.XMLSyntaxError:
        print(stream.getvalue(), file=sys.stderr)
        raise
