# Copyright 2019 128 Technology, Inc.

import os
import contextlib
import sys
import runpy
import pytest
import io

import pyang
from lxml import etree

from yinsolidated.plugin import plugin

YINSOLIDATED_PLUGIN_DIRECTORY = os.path.dirname(plugin.__file__)


def pytest_addoption(parser):
    parser.addoption("--pyang-path", action="store",
                     help="path to pyang executable")


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

    sys.argv = [pyang_path] + pyang_args

    stream = io.StringIO()
    try:
        with contextlib.redirect_stdout(stream):
            runpy.run_path(pyang_path, run_name="__main__")
    except SystemExit as err:
        if err.code != 0:
            raise

    try:
        return etree.fromstring(stream.getvalue().encode("utf-8"))
    except etree.XMLSyntaxError:
        print(stream.getvalue(), file=sys.stderr)
        raise
