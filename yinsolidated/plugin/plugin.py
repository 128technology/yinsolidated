###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""
Pyang plugin that generates a single, consolidated XML representation of a YANG
data model

Usage
=====
pyang -f yinsolidated <main-module>.yang <augmenting-module>.yang ...

NOTE: the main module MUST be passed as the first positional argument
"""

from __future__ import unicode_literals

from lxml import etree
from pyang import (
    plugin,
    statements,
    syntax,
    yin_parser,
    __version__ as pyang_version
)

from yinsolidated import _common


_EXTRA_PYANG_DATA_KEYWORDS = [
    'notification',
    'rpc',
    'input',
    'output'
]

_RESOLVED_KEYWORDS = [
    'grouping',
    'import',
    'include',
    'typedef'
]

_DATA_KEYWORDS = (
    _common.DATA_DEFINITION_KEYWORDS +
    _EXTRA_PYANG_DATA_KEYWORDS +
    _RESOLVED_KEYWORDS
)


def pyang_plugin_init():
    """Required function definition for Pyang to register the plugin"""

    plugin.register_plugin(ConsolidatedModelPlugin())


class ConsolidatedModelPlugin(plugin.PyangPlugin):

    """The plugin class to register with Pyang"""

    # Disable this check because pyang's argument names are ugly
    # pylint: disable=arguments-differ

    def add_output_format(self, formats):
        self.multiple_modules = True
        formats['yinsolidated'] = self

    def emit(self, _, modules, output):
        model = _build_consolidated_model(modules)

        document = etree.tostring(
            model,
            xml_declaration=True,
            pretty_print=True
        ).decode('UTF-8')

        output.write(document)


def _build_consolidated_model(modules):
    main_module = modules[0]
    module_element = _make_builtin_yin_element_recursive(main_module)

    _add_external_identities(modules[1:], module_element)

    return module_element


def _make_builtin_yin_element_recursive(statement, parent_elem=None):
    yin_element = _make_builtin_yin_element(statement, parent_elem)
    _append_children(statement, yin_element)
    return yin_element


def _make_builtin_yin_element(statement, parent_elem):
    try:
        argument_name, is_arg_yin_element = syntax.yin_map[statement.keyword]
    except KeyError:
        raise InvalidKeywordError(statement.keyword)

    module_prefix = None
    nsmap = {'yin': yin_parser.yin_namespace}

    if statement.keyword == 'module':
        module_prefix = statement.i_prefix
        nsmap.update(_get_module_nsmap(statement))
    elif (_is_augmenting_another_module(statement) or
          statement.keyword == 'identity'):
        module_prefix = statement.i_module.i_prefix
        nsmap.update(_get_module_nsmap(statement.i_module))

    tag = etree.QName(yin_parser.yin_namespace, statement.keyword)

    yin_element = (etree.Element(tag, nsmap=nsmap) if parent_elem is None else
                   etree.SubElement(parent_elem, tag, nsmap=nsmap))

    _add_statement_argument(
        argument_name, statement.arg, yin_parser.yin_namespace,
        is_arg_yin_element, yin_element)

    if module_prefix is not None:
        yin_element.set('module-prefix', module_prefix)

    return yin_element


class InvalidKeywordError(Exception):

    """A YANG statement has an invalid keyword"""

    def __init__(self, keyword):
        super(InvalidKeywordError, self).__init__(
            "Invalid keyword '{}'".format(keyword))


def _is_augmenting_another_module(statement):
    return (_is_augmenting(statement) and
            statement.i_module.i_modulename !=
            statement.i_augment.i_target_node.i_module.i_modulename)


def _is_augmenting(statement):
    return (hasattr(statement, 'i_augment') and
            statement.i_augment is not None)


def _get_module_nsmap(module_statement):
    nsmap = {}

    prefixes = module_statement.i_prefixes
    for prefix, (module_name, revision) in prefixes.items():
        imported_module_statement = statements.modulename_to_module(
            module_statement, module_name, revision)
        namespace = imported_module_statement.search_one('namespace').arg
        nsmap[prefix] = namespace

    return nsmap


def _add_statement_argument(arg_name, arg_value, namespace, is_element,
                            yin_element):
    if arg_name is not None:
        if is_element:
            tag = etree.QName(namespace, arg_name)
            arg_element = etree.SubElement(yin_element, tag)
            arg_element.text = arg_value
        else:
            yin_element.set(arg_name, arg_value)


def _append_children(statement, yin_element):
    for sub_statement in _iterate_non_data_sub_statements(statement):
        _make_yin_element_recursive(sub_statement, yin_element)

    _append_inherited_if_feature_elements(statement, yin_element)
    _append_inherited_when_elements(statement, yin_element)

    if statement.keyword == 'type':
        _append_children_for_type(statement, yin_element)

    if hasattr(statement, 'i_children'):
        for data_definition in statement.i_children:
            _make_yin_element_recursive(data_definition, yin_element)


def _iterate_non_data_sub_statements(statement):
    for sub_statement in statement.substmts:
        if sub_statement.keyword not in _DATA_KEYWORDS:
            yield sub_statement


def _append_inherited_if_feature_elements(statement, yin_element):
    if _is_augmenting(statement) and pyang_version >= '1.7.1':
        _append_if_feature_elements_from_augment(
            statement.i_augment,
            yin_element
        )

    if _is_member_of_grouping(statement):
        _append_if_feature_elements_from_uses(statement.i_uses, yin_element)


def _append_if_feature_elements_from_augment(augment_statement, yin_element):
    for if_feature_statement in augment_statement.search('if-feature'):
        _make_builtin_yin_element(if_feature_statement, yin_element)


def _is_member_of_grouping(statement):
    return (_common.is_data_definition(statement.keyword) and
            hasattr(statement, 'i_uses') and
            statement.i_uses is not None)


def _append_if_feature_elements_from_uses(uses_statements, yin_element):
    for uses_statement in uses_statements:
        for if_feature_statement in uses_statement.search('if-feature'):
            _make_builtin_yin_element(if_feature_statement, yin_element)


def _append_inherited_when_elements(statement, yin_element):
    if _is_augmenting(statement):
        _append_when_elements_from_augment(statement.i_augment, yin_element)

    if _is_member_of_grouping(statement):
        _append_when_elements_from_uses(statement.i_uses, yin_element)


def _append_when_elements_from_augment(augment_statement, yin_element):
    when_statements = augment_statement.search('when')
    _append_when_elements_with_parent_context(when_statements, yin_element)


def _append_when_elements_with_parent_context(when_statements, yin_element):
    for when_statement in when_statements:
        when_element = _make_builtin_yin_element(when_statement, yin_element)
        when_element.set('context-node', 'parent')


def _append_when_elements_from_uses(uses_statements, yin_element):
    for uses_statement in uses_statements:
        when_statements = uses_statement.search('when')
        _append_when_elements_with_parent_context(when_statements, yin_element)


def _append_children_for_type(type_statement, yin_element):
    if _is_typedef(type_statement):
        _make_yin_element_recursive(type_statement.i_typedef,
                                    parent_elem=yin_element)

    data_node = type_statement.parent
    if _has_leafref_pointer(data_node):
        referenced_leaf, _ = data_node.i_leafref_ptr
        referenced_type_statement = referenced_leaf.search_one('type')
        _make_yin_element_recursive(referenced_type_statement,
                                    parent_elem=yin_element)


def _is_typedef(type_statement):
    return (hasattr(type_statement, 'i_typedef') and
            type_statement.i_typedef is not None)


def _has_leafref_pointer(data_node):
    return (hasattr(data_node, 'i_leafref_ptr') and
            data_node.i_leafref_ptr is not None)


def _make_yin_element_recursive(statement, parent_elem):
    if hasattr(statement, 'i_extension'):
        _make_extension_element(statement, parent_elem)
    else:
        _make_builtin_yin_element_recursive(statement, parent_elem=parent_elem)


def _make_extension_element(statement, parent_elem):
    extension_module = statement.i_extension.i_module
    namespace = extension_module.search_one('namespace').arg

    prefix, keyword = statement.raw_keyword
    tag = etree.QName(namespace, keyword)
    nsmap = {prefix: namespace}

    extension_element = etree.SubElement(parent_elem, tag, nsmap=nsmap)
    extension_element.text = statement.arg


def _add_external_identities(augmenting_modules, module_element):
    for module in augmenting_modules:
        for identity in module.i_identities.values():
            _make_builtin_yin_element_recursive(identity, module_element)
