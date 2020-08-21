# Copyright 2016 128 Technology, Inc.

"""
Pyang plugin that generates a single, consolidated XML representation of a YANG
data model

Usage
=====
pyang -f yinsolidated <main-module>.yang <augmenting-module>.yang ...

NOTE: the main module MUST be passed as the first positional argument
"""

from __future__ import unicode_literals

import json
import optparse

from lxml import etree
from pyang import __version__ as pyang_version, plugin, statements, syntax, yin_parser

from yinsolidated import _common


_EXTRA_PYANG_DATA_KEYWORDS = ["notification", "rpc", "input", "output"]

_RESOLVED_KEYWORDS = ["grouping", "import", "include", "typedef"]

_DATA_KEYWORDS = (
    _common.DATA_DEFINITION_KEYWORDS + _EXTRA_PYANG_DATA_KEYWORDS + _RESOLVED_KEYWORDS
)


def pyang_plugin_init():
    """Required function definition for Pyang to register the plugin"""

    plugin.register_plugin(ConsolidatedModelPlugin())


class ConsolidatedModelPlugin(plugin.PyangPlugin):

    """The plugin class to register with Pyang"""

    # Disable this check because pyang's argument names are ugly
    # pylint: disable=arguments-differ

    def add_opts(self, optparser):
        """Override."""
        optparser.add_options(
            [
                optparse.make_option(
                    "--yinsolidated-output-format",
                    dest="yinsoldated_output_format",
                    choices=["xml", "json"],
                    default="xml",
                    help="The format of the output model",
                ),
            ]
        )

    def add_output_format(self, formats):
        """Override."""
        self.multiple_modules = True
        formats["yinsolidated"] = self

    def emit(self, ctx, modules, output):
        """Override."""
        fmt = ctx.opts.yinsoldated_output_format
        model = _build_consolidated_model(modules, fmt)

        document = (
            etree.tostring(model, xml_declaration=True, pretty_print=True).decode(
                "UTF-8"
            )
            if fmt == "xml"
            else json.dumps(model, indent=2)
        )

        output.write(document)


def _build_consolidated_model(modules, fmt):
    main_module = modules[0]
    module_element = _make_builtin_yin_element_recursive(main_module, fmt=fmt)

    _add_external_identities(modules[1:], module_element, fmt)

    return module_element


def _make_builtin_yin_element_recursive(statement, parent_elem=None, fmt="xml"):
    yin_element = _make_builtin_yin_element(statement, parent_elem, fmt)
    _append_children(statement, yin_element, fmt)
    return yin_element


def _make_builtin_yin_element(statement, parent_elem, fmt):
    try:
        argument_name, is_arg_yin_element = syntax.yin_map[statement.keyword]
    except KeyError:
        raise InvalidKeywordError(statement.keyword)

    module_name = None
    module_prefix = None
    nsmap = {}

    if statement.keyword == "module":
        module_name = statement.i_modulename
        module_prefix = statement.i_prefix
        nsmap["yin"] = yin_parser.yin_namespace
        nsmap.update(_get_module_nsmap(statement))
    elif _is_augmenting_another_module(statement) or statement.keyword == "identity":
        module_name = statement.i_module.i_modulename
        module_prefix = statement.i_module.i_prefix
        nsmap.update(_get_module_nsmap(statement.i_module))

    if fmt == "xml":
        tag = etree.QName(yin_parser.yin_namespace, statement.keyword)
        yin_element = (
            etree.Element(tag, nsmap=nsmap)
            if parent_elem is None
            else etree.SubElement(parent_elem, tag, nsmap=nsmap)
        )
    else:
        yin_element = _JsonElement(
            keyword=statement.keyword,
            namespace=yin_parser.yin_namespace,
            parent_elem=parent_elem,
            nsmap=nsmap,
        )

    _add_statement_argument(
        argument_name,
        statement.arg,
        yin_parser.yin_namespace,
        is_arg_yin_element,
        yin_element,
        fmt,
    )

    if module_prefix is not None:
        yin_element.set("module-prefix", module_prefix)

    if module_name is not None:
        yin_element.set("module-name", module_name)

    return yin_element


class _JsonElement(dict):
    def __init__(self, keyword, namespace, nsmap, parent_elem):
        super(_JsonElement, self).__init__(keyword=keyword, namespace=namespace)

        if parent_elem is not None:
            parent_elem["children"].append(self)

        if nsmap:
            self["nsmap"] = nsmap

    @property
    def text(self):
        """Compatibility shim to mimic an etree.Element."""
        return self["text"]

    @text.setter
    def text(self, value):
        """Compatibility shim to mimic an etree.Element."""
        self["text"] = value

    def __missing__(self, key):
        # lazily create the children sub-list.
        if key == "children":
            return self.setdefault(key, [])
        raise KeyError(key)

    def set(self, key, value):
        """Compatibility shim to mimic an etree.Element."""
        self[key] = value


class InvalidKeywordError(Exception):

    """A YANG statement has an invalid keyword"""

    def __init__(self, keyword):
        super(InvalidKeywordError, self).__init__(
            "Invalid keyword '{}'".format(keyword)
        )


def _is_augmenting_another_module(statement):
    return (
        _is_augmenting(statement)
        and statement.i_module.i_modulename
        != statement.i_augment.i_target_node.i_module.i_modulename
    )


def _is_augmenting(statement):
    return hasattr(statement, "i_augment") and statement.i_augment is not None


def _get_module_nsmap(module_statement):
    nsmap = {}

    prefixes = module_statement.i_prefixes
    for prefix, (module_name, revision) in prefixes.items():
        imported_module_statement = statements.modulename_to_module(
            module_statement, module_name, revision
        )
        namespace = imported_module_statement.search_one("namespace").arg
        nsmap[prefix] = namespace

    return nsmap


def _add_statement_argument(
    arg_name, arg_value, namespace, is_element, yin_element, fmt
):
    if arg_name is None:
        return

    if is_element:
        if fmt == "xml":
            tag = etree.QName(namespace, arg_name)
            arg_element = etree.SubElement(yin_element, tag)
            arg_element.text = arg_value
        else:
            yin_element[arg_name] = arg_value
    else:
        yin_element.set(arg_name, arg_value)


def _append_children(statement, yin_element, fmt):
    for sub_statement in _iterate_non_data_sub_statements(statement):
        _make_yin_element_recursive(sub_statement, yin_element, fmt)

    _append_inherited_if_feature_elements(statement, yin_element, fmt)
    _append_inherited_when_elements(statement, yin_element, fmt)

    if statement.keyword == "type":
        _append_children_for_type(statement, yin_element, fmt)

    if hasattr(statement, "i_children"):
        for data_definition in statement.i_children:
            _make_yin_element_recursive(data_definition, yin_element, fmt)


def _iterate_non_data_sub_statements(statement):
    for sub_statement in statement.substmts:
        if sub_statement.keyword not in _DATA_KEYWORDS:
            yield sub_statement


def _append_inherited_if_feature_elements(statement, yin_element, fmt):
    if _is_augmenting(statement) and pyang_version >= "1.7.1":
        _append_if_feature_elements_from_augment(statement.i_augment, yin_element, fmt)

    if _is_member_of_grouping(statement):
        _append_if_feature_elements_from_uses(statement.i_uses, yin_element, fmt)


def _append_if_feature_elements_from_augment(augment_statement, yin_element, fmt):
    for if_feature_statement in augment_statement.search("if-feature"):
        _make_builtin_yin_element(if_feature_statement, yin_element, fmt)


def _is_member_of_grouping(statement):
    return (
        _common.is_data_definition(statement.keyword)
        and hasattr(statement, "i_uses")
        and statement.i_uses is not None
    )


def _append_if_feature_elements_from_uses(uses_statements, yin_element, fmt):
    for uses_statement in uses_statements:
        for if_feature_statement in uses_statement.search("if-feature"):
            _make_builtin_yin_element(if_feature_statement, yin_element, fmt)


def _append_inherited_when_elements(statement, yin_element, fmt):
    if _is_augmenting(statement):
        _append_when_elements_from_augment(statement.i_augment, yin_element, fmt)

    if _is_member_of_grouping(statement):
        _append_when_elements_from_uses(statement.i_uses, yin_element, fmt)


def _append_when_elements_from_augment(augment_statement, yin_element, fmt):
    when_statements = augment_statement.search("when")
    _append_when_elements_with_parent_context(when_statements, yin_element, fmt)


def _append_when_elements_with_parent_context(when_statements, yin_element, fmt):
    for when_statement in when_statements:
        when_element = _make_builtin_yin_element(when_statement, yin_element, fmt)
        when_element.set("context-node", "parent")


def _append_when_elements_from_uses(uses_statements, yin_element, fmt):
    for uses_statement in uses_statements:
        when_statements = uses_statement.search("when")
        _append_when_elements_with_parent_context(when_statements, yin_element, fmt)


def _append_children_for_type(type_statement, yin_element, fmt):
    if _is_typedef(type_statement):
        _make_yin_element_recursive(
            type_statement.i_typedef, parent_elem=yin_element, fmt=fmt
        )

    data_node = type_statement.parent
    if _has_leafref_pointer(data_node):
        referenced_leaf, _ = data_node.i_leafref_ptr
        referenced_type_statement = referenced_leaf.search_one("type")
        _make_yin_element_recursive(
            referenced_type_statement, parent_elem=yin_element, fmt=fmt
        )


def _is_typedef(type_statement):
    return hasattr(type_statement, "i_typedef") and type_statement.i_typedef is not None


def _has_leafref_pointer(data_node):
    return hasattr(data_node, "i_leafref_ptr") and data_node.i_leafref_ptr is not None


def _make_yin_element_recursive(statement, parent_elem, fmt):
    if hasattr(statement, "i_extension"):
        _make_extension_element(statement, parent_elem, fmt)
    else:
        _make_builtin_yin_element_recursive(statement, parent_elem=parent_elem, fmt=fmt)


def _make_extension_element(statement, parent_elem, fmt):
    extension_module = statement.i_extension.i_module
    namespace = extension_module.search_one("namespace").arg

    prefix, keyword = statement.raw_keyword
    tag = etree.QName(namespace, keyword)
    nsmap = {prefix: namespace}

    if fmt == "xml":
        extension_element = etree.SubElement(parent_elem, tag, nsmap=nsmap)
    else:
        extension_element = _JsonElement(
            keyword=keyword, namespace=namespace, nsmap=nsmap, parent_elem=parent_elem,
        )

    if _is_complex_extension(statement.i_extension):
        argument_name, is_arg_yin_element = _get_exension_argument_details(
            statement.i_extension
        )
        _add_statement_argument(
            argument_name,
            statement.arg,
            namespace,
            is_arg_yin_element,
            extension_element,
            fmt,
        )
        _append_children(statement, extension_element, fmt)
    else:
        extension_element.text = statement.arg


def _is_complex_extension(extension_statement):
    extension_description = extension_statement.search_one("description")
    return (
        extension_description is not None and "#yinformat" in extension_description.arg
    )


def _get_exension_argument_details(extension_statement):
    argument_statement = extension_statement.search_one("argument")
    if argument_statement is None:
        return None, False

    argument_name = argument_statement.arg

    yin_element_statement = argument_statement.search_one("yin-element")
    is_arg_yin_element = (
        yin_element_statement is not None and yin_element_statement.arg == "true"
    )

    return argument_name, is_arg_yin_element


def _add_external_identities(augmenting_modules, module_element, fmt):
    for module in augmenting_modules:
        for identity in module.i_identities.values():
            _make_builtin_yin_element_recursive(identity, module_element, fmt)
