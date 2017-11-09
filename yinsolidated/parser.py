###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""
Parses the YINsolidated model into an lxml.etree.ElementTree containing custom
lxml.etree.Element subclasses for each type of YANG statement. These custom
classes provide convenient methods and properties for accessing YANG-specific
data without interacting with the XML directly.
"""

# TODO(athompson): remove after resolving issue #7
# pylint: disable=missing-docstring

from __future__ import unicode_literals

import re

import xpathparser
from lxml import etree

from yinsolidated import _common


_NSMAP = {'yin': _common.YIN_NS}

_DATA_NODE_PREDICATE = ' or '.join(
    'self::yin:{}'.format(keyword)
    for keyword in _common.DATA_NODE_KEYWORDS
)


class Error(Exception):

    """Base exception"""


class _ConsolidatedModelLookup(etree.CustomElementClassLookup):

    def lookup(self, _node_type, _document, namespace, name):
        return (_get_yin_element_class(name)
                if namespace == _common.YIN_NS
                else None)


def _get_yin_element_class(name):
    yin_element_class_map = {
        'module': ModuleElement,
        'rpc': RpcElement,
        'container': ContainerElement,
        'leaf': LeafElement,
        'leaf-list': LeafListElement,
        'list': ListElement,
        'anyxml': AnyxmlElement,
        'type': TypeElement,
        'typedef': TypedefElement,
        'bit': BitElement,
        'enum': EnumElement,
        'pattern': PatternElement,
        'when': WhenElement,
        'identity': IdentityElement
    }

    try:
        element_class = yin_element_class_map[name]
    except KeyError:
        if _common.is_data_definition(name):
            element_class = DataDefinitionElement
        else:
            element_class = YinElement

    return element_class


# Custom XML parser to use for the YINsolidated model
CONSOLIDATED_MODEL_PARSER = etree.XMLParser()
CONSOLIDATED_MODEL_PARSER.set_element_class_lookup(_ConsolidatedModelLookup())


def parse(path):
    """Parses the YINsolidated model file at the given *path*"""
    return etree.parse(path, parser=CONSOLIDATED_MODEL_PARSER)


def fromstring(xml_string):
    """Parses the given string as the YINsolidated model"""
    return etree.fromstring(xml_string, parser=CONSOLIDATED_MODEL_PARSER)


class YinElement(etree.ElementBase):

    @property
    def keyword(self):
        return etree.QName(self.tag).localname

    @property
    def namespace(self):
        return self.nsmap[self.prefix]

    @property
    def prefix(self):
        ancestor_prefixes = self.xpath(
            'ancestor-or-self::yin:*[@module-prefix]/@module-prefix',
            namespaces=_NSMAP
        )
        try:
            return ancestor_prefixes[-1]
        except IndexError:
            raise MissingPrefixError(self)

    @property
    def namespace_map(self):
        return {
            prefix: namespace
            for prefix, namespace in self.nsmap.items()
            if prefix is not None
        }

    @property
    def description(self):
        description = self.findtext('yin:description/yin:text',
                                    namespaces=_NSMAP)

        if description is not None:
            description = _change_all_whitespace_to_spaces(description)

        return description

    def iterate_data_definitions(self):
        for child in self:
            if _common.is_data_definition(etree.QName(child.tag).localname):
                yield child

    def iterate_rpcs(self):
        for child in self:
            if etree.QName(child.tag).localname == 'rpc':
                yield child

    def get_ancestor_data_nodes(self):
        return self.xpath(
            'ancestor::*[{}]'.format(_DATA_NODE_PREDICATE),
            namespaces=_NSMAP
        )

    def get_ancestor_or_self_data_nodes(self):
        return self.xpath(
            'ancestor-or-self::*[{}]'.format(_DATA_NODE_PREDICATE),
            namespaces=_NSMAP
        )


def _change_all_whitespace_to_spaces(string):
    return re.sub(r'\s+', ' ', string).strip()


class MissingPrefixError(Error):

    """Could not find a prefix attribute"""

    def __init__(self, data_def_element):
        message = "No prefix attribute found for ancestors of {} '{}'".format(
            data_def_element.keyword,
            data_def_element.name
        )
        super(MissingPrefixError, self).__init__(message)


class ModuleElement(YinElement):

    @property
    def name(self):
        return self.get('name')


class DefinitionElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def status(self):
        return _get_status(self)


class RpcElement(DefinitionElement):

    @property
    def input(self):
        return self.find('yin:input', namespaces=_NSMAP)

    @property
    def output(self):
        return self.find('yin:output', namespaces=_NSMAP)


class DataDefinitionElement(DefinitionElement):

    @property
    def is_config(self):
        return self.xpath(
            'count(ancestor-or-self::yin:*[yin:config/@value = "false"]) = 0',
            namespaces=_NSMAP)

    @property
    def when_elements(self):
        return self.findall('yin:when', namespaces=_NSMAP)


class ContainerElement(DataDefinitionElement):

    @property
    def presence(self):
        return _get_subelem_attribute_or_default(self, 'presence', 'value')


def _get_subelem_attribute_or_default(data_def_element, subelem_name,
                                      attr_name, default=None):
    element = data_def_element.find('yin:{}'.format(subelem_name),
                                    namespaces=_NSMAP)
    return element.get(attr_name) if element is not None else default


class LeafElement(DataDefinitionElement):

    @property
    def type(self):
        return _get_type(self)

    @property
    def default(self):
        return _get_default(self)

    @property
    def units(self):
        return _get_units(self)

    @property
    def is_mandatory(self):
        return _is_mandatory(self)

    @property
    def is_list_key(self):
        return ((self.getparent() is not None) and
                (self.getparent().keyword == 'list') and
                ((self.name, self.namespace) in self.getparent().key_ids))


def _get_type(element):
    return element.find('yin:type', namespaces=_NSMAP)


def _get_status(element):
    return _get_subelem_attribute_or_default(
        element, 'status', 'value', default='current')


def _get_default(element):
    return _get_subelem_attribute_or_default(element, 'default', 'value')


def _get_units(element):
    return _get_subelem_attribute_or_default(element, 'units', 'name')


def _is_mandatory(element):
    mandatory_string = _get_subelem_attribute_or_default(
        element, 'mandatory', 'value', default='false')
    return mandatory_string == 'true'


class LeafListElement(DataDefinitionElement):

    @property
    def type(self):
        return _get_type(self)

    @property
    def units(self):
        return _get_units(self)

    @property
    def min_elements(self):
        return _get_min_elements(self)

    @property
    def max_elements(self):
        return _get_max_elements(self)

    @property
    def ordered_by(self):
        return _get_ordered_by(self)


def _get_min_elements(data_def_element):
    min_elements_string = _get_subelem_attribute_or_default(
        data_def_element, 'min-elements', 'value', default='0')
    return int(min_elements_string)


def _get_max_elements(data_def_element):
    max_elements_string = _get_subelem_attribute_or_default(
        data_def_element, 'max-elements', 'value', default='unbounded')
    return (None if max_elements_string == 'unbounded'
            else int(max_elements_string))


def _get_ordered_by(data_def_element):
    return _get_subelem_attribute_or_default(
        data_def_element, 'ordered-by', 'value', default='system')


class ListElement(DataDefinitionElement):

    @property
    def key_ids(self):
        keys = []

        key_string = self.xpath('string(yin:key/@value)', namespaces=_NSMAP)
        for key_identifier in key_string.split():
            if ':' in key_identifier:
                prefix, name = key_identifier.split(':')
                namespace = self.nsmap[prefix]
            else:
                name = key_identifier
                namespace = self.namespace

            keys.append((name, namespace))

        return keys

    @property
    def unique(self):
        unique_str = _get_subelem_attribute_or_default(
            self, 'unique', 'tag', '')
        return unique_str.split()

    @property
    def min_elements(self):
        return _get_min_elements(self)

    @property
    def max_elements(self):
        return _get_max_elements(self)

    @property
    def ordered_by(self):
        return _get_ordered_by(self)


class AnyxmlElement(DataDefinitionElement):

    @property
    def is_mandatory(self):
        return _is_mandatory(self)


class TypeElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def unprefixed_name(self):
        return self.name.split(':')[-1]

    @property
    def prefix(self):
        if ':' in self.name:
            return self.name.split(':')[0]

        return super(TypeElement, self).prefix

    @property
    def base_type(self):
        typedef_elem = self.typedef
        return self if typedef_elem is None else typedef_elem.type.base_type

    @property
    def typedef(self):
        return self.find('yin:typedef', namespaces=_NSMAP)

    @property
    def bits(self):
        return self.base_type.findall('yin:bit', namespaces=_NSMAP)

    @property
    def enums(self):
        return self.base_type.findall('yin:enum', namespaces=_NSMAP)

    @property
    def fraction_digits(self):
        return _get_subelem_attribute_or_default(
            self.base_type, 'fraction-digits', 'value')

    @property
    def length(self):
        range_value = _get_subelem_attribute_or_default(
            self, 'length', 'value'
        )

        if range_value is None and self.typedef is not None:
            range_value = self.typedef.type.length

        return range_value

    @property
    def path(self):
        return _get_subelem_attribute_or_default(
            self.base_type, 'path', 'value')

    @property
    def patterns(self):
        return self.base_type.findall('yin:pattern', namespaces=_NSMAP)

    @property
    def range(self):
        range_value = _get_subelem_attribute_or_default(
            self, 'range', 'value'
        )

        if range_value is None and self.typedef is not None:
            range_value = self.typedef.type.range

        return range_value

    @property
    def referenced_type(self):
        base_type_elem = self.base_type
        return (base_type_elem.find('yin:type', namespaces=_NSMAP)
                if base_type_elem.name == 'leafref' else None)

    @property
    def subtypes(self):
        base_type_elem = self.base_type
        return (base_type_elem.findall('yin:type', namespaces=_NSMAP)
                if base_type_elem.name == 'union' else [])

    @property
    def base_identity(self):
        return _get_subelem_attribute_or_default(
            self.base_type, 'base', 'name')

    def get_identities(self):
        return list(self.iterate_identities())

    def iterate_identities(self):
        base = self.base_identity

        if base is not None:
            base_elem = self._find_identity(base)

            for identity_elem in base_elem.iterate_derived_identities():
                yield identity_elem

    def _find_identity(self, identity):
        root = self.getroottree()
        data_node = self.getparent()

        identifier_to_find = _parse_identifier(
            identity, data_node.namespace_map, data_node.namespace)

        for identity_elem in root.iterfind('yin:identity', namespaces=_NSMAP):
            identifier = (identity_elem.name, identity_elem.namespace)
            if identifier == identifier_to_find:
                return identity_elem

        raise MissingIdentityError(*identifier_to_find)


def _parse_identifier(identifier, nsmap, default_namespace):
    if ':' in identifier:
        prefix, name = identifier.split(':')
        namespace = nsmap[prefix]
    else:
        name = identifier
        namespace = default_namespace

    return name, namespace


class MissingIdentityError(Error):

    def __init__(self, name, namespace):
        super(MissingIdentityError, self).__init__(
            'Could not find identity {} in namespace {}'.format(
                name, namespace))


class TypedefElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def type(self):
        return _get_type(self)

    @property
    def default(self):
        return _get_default(self)

    @property
    def units(self):
        return _get_units(self)


class BitElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def position(self):
        position = _get_subelem_attribute_or_default(self, 'position', 'value')
        return int(position) if position is not None else None


class EnumElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def value(self):
        value = _get_subelem_attribute_or_default(self, 'value', 'value')
        return int(value) if value is not None else None


class PatternElement(YinElement):

    @property
    def value(self):
        return self.get('value')

    @property
    def error_message(self):
        return self.findtext('yin:error-message/yin:value', namespaces=_NSMAP)


class WhenElement(YinElement):

    @property
    def condition(self):
        data_def_element = self.getparent()
        assert hasattr(data_def_element, 'prefix'), (
            "Parent of 'when' element is not a data definition element"
        )

        prefix = data_def_element.prefix
        return _ensure_xpath_names_prefixed(self.get('condition'), prefix)

    @property
    def context_node_is_parent(self):
        return self.get('context-node') == 'parent'


def _ensure_xpath_names_prefixed(expression, prefix):
    tokens = xpathparser.tokens(expression)
    new_tokens = []

    for token_type, token in tokens:
        if token_type == 'name' and ':' not in token:
            new_tokens.append('{}:{}'.format(prefix, token))
        else:
            new_tokens.append(token)

    return ''.join(new_tokens)


class IdentityElement(YinElement):

    @property
    def name(self):
        return self.get('name')

    @property
    def base(self):
        base = _get_subelem_attribute_or_default(self, 'base', 'name')

        if base is None:
            name = None
            namespace = None
        else:
            name, namespace = _parse_identifier(
                base, self.namespace_map, self.namespace)

        return name, namespace

    def get_derived_identities(self):
        return list(self.iterate_derived_identities())

    def iterate_derived_identities(self):
        for identity_elem in self._iterate_directly_derived_identities():
            yield identity_elem
            for nested_identity in identity_elem.iterate_derived_identities():
                yield nested_identity

    def _iterate_directly_derived_identities(self):
        root = self.getroottree()
        for identity_elem in root.iterfind('yin:identity', namespaces=_NSMAP):
            if identity_elem.base == (self.name, self.namespace):
                yield identity_elem
