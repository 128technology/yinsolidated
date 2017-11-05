###############################################################################
# Copyright (c) 2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""Shared constants and utilities"""

YIN_NS = 'urn:ietf:params:xml:ns:yang:yin:1'


# [RFC 6020 Section 3]

DATA_NODE_KEYWORDS = [
    'container',
    'leaf',
    'leaf-list',
    'list',
    'anyxml'
]

DATA_DEFINITION_KEYWORDS = DATA_NODE_KEYWORDS + [
    'choice',
    'case',
    'augment',
    'uses'
]


def is_data_node(keyword):
    """Returns True if *keyword* is a YANG data node keyword"""
    return keyword in DATA_NODE_KEYWORDS


def is_data_definition(keyword):
    """Returns True if *keyword* is a YANG data definition keyword"""
    return keyword in DATA_DEFINITION_KEYWORDS
