# Copyright 2017 128 Technology, Inc.

"""Unit tests for the _common module"""

import pytest

from yinsolidated import _common


@pytest.mark.parametrize('keyword', [
    'container',
    'leaf',
    'leaf-list',
    'list',
    'anyxml'
])
def test_is_data_node(keyword):
    assert _common.is_data_node(keyword)


@pytest.mark.parametrize('keyword', [
    'choice',
    'case',
    'augment',
    'uses',
    'module',
    'rpc',
    'identity',
    'foo'
])
def test_is_not_data_node(keyword):
    assert not _common.is_data_node(keyword)


@pytest.mark.parametrize('keyword', [
    'container',
    'leaf',
    'leaf-list',
    'list',
    'anyxml',
    'choice',
    'case',
    'augment',
    'uses'
])
def test_is_data_definition(keyword):
    assert _common.is_data_definition(keyword)


@pytest.mark.parametrize('keyword', [
    'module',
    'rpc',
    'identity',
    'foo'
])
def test_is_not_data_definition(keyword):
    assert not _common.is_data_definition(keyword)
