# Copyright 2020 128 Technology, Inc.

"""
Parses the YINsolidated model into an JSON document containing custom dict subclasses
for each type of YANG statement. These custom classes provide convenientmethods and
properties for accessing YANG-specific data without interacting with the XML directly.
"""

# TODO: remove after resolving issue #7
# pylint: disable=missing-docstring

from __future__ import unicode_literals

import json
import re

import xpathparser

from yinsolidated import _common, _error


_YIN = "urn:ietf:params:xml:ns:yang:yin:1"


def parse(contents):
    """Parse the YINsolidated model from JSON or a string."""
    contents = json.loads(contents) if isinstance(contents, str) else contents
    return _parse(contents)


def _parse(raw, parent=None):
    if not isinstance(raw, dict):
        raise _error.Error(
            "expected dict, got {type}: {value}".format(type=type(raw), value=raw)
        )
    cls = _get_yin_element_class(raw.get("keyword"))
    children = raw.pop("children", [])
    parsed = cls(raw, parent=parent)
    for child in children:
        _parse(child, parent=parsed)
    return parsed


def _get_yin_element_class(name):
    yin_element_class_map = {
        "module": ModuleElement,
        "container": ContainerElement,
        "leaf": LeafElement,
        "leaf-list": LeafListElement,
        "list": ListElement,
        "anyxml": AnyxmlElement,
        "type": TypeElement,
        "typedef": TypedefElement,
        "bit": BitElement,
        "enum": EnumElement,
        "pattern": PatternElement,
        "when": WhenElement,
        "identity": IdentityElement,
    }

    try:
        element_class = yin_element_class_map[name]
    except KeyError:
        if _common.is_data_definition(name):
            element_class = DataDefinitionElement
        else:
            element_class = YinElement

    return element_class


class YinElement(dict):
    def __init__(self, data, parent=None):
        super(YinElement, self).__init__(data)
        self._parent = parent

        if parent:
            parent.setdefault("children", []).append(self)

    @property
    def parent(self):
        return self._parent

    @property
    def keyword(self):
        return self.get("keyword")

    @property
    def name(self):
        return self.get("name")

    @property
    def nsmap(self):
        return self.get("nsmap") or {}

    @property
    def namespace_map(self):
        nsmap = {}
        for element in self.iter_parents(include_self=True):
            nsmap.update(element.nsmap)
        return nsmap

    @property
    def namespace(self):
        prefix = self.prefix
        for element in self.iter_parents(include_self=True):
            try:
                return element.nsmap[prefix]
            except KeyError:
                pass

        raise _error.MissingNamespaceError(self)

    @property
    def children(self):
        return self.get("children") or []

    @property
    def module_name(self):
        for parent in self.iter_parents(include_self=True):
            try:
                return parent["module-name"]
            except KeyError:
                pass

        raise _error.MissingModuleNameError(self)

    @property
    def prefix(self):
        for parent in self.iter_parents(include_self=True):
            try:
                return parent["module-prefix"]
            except KeyError:
                pass

        raise _error.MissingPrefixError(self)

    @property
    def description(self):
        node = self.find("description", namespace=_YIN)
        description = node["text"] if node is not None else None

        if description is not None:
            description = _change_all_whitespace_to_spaces(description)

        return description

    def iterate_data_definitions(self):
        for child in self.children:
            if _common.is_data_definition(child.keyword):
                yield child

    def get_ancestor_data_nodes(self):
        return [
            parent
            for parent in reversed(list(self.iter_parents()))
            if _common.is_data_node(parent.keyword)
        ]

    def iter_parents(self, include_self=False):
        current = self if include_self else self.parent

        while current is not None:
            yield current
            current = current.parent

    def get_ancestor_or_self_data_nodes(self):
        return [
            node
            for node in reversed(list(self.iter_parents(include_self=True)))
            if _common.is_data_node(node.keyword)
        ]

    # the following functions mimic some of the common etree.Element functions

    def find(self, keyword, namespace=None):
        for child in self.children:
            if child._is_match(keyword, namespace):  # pylint: disable=protected-access
                return child
        return None

    def _is_match(self, keyword, namespace):
        if self.keyword != keyword:
            return False
        # NOTE: This is not equivalent to *self.namespace*. This is the namespace of the
        # *keyword*, not of the *YinElement*.
        return namespace is None or namespace == self.get("namespace")

    def iterfind(self, keyword, namespace=None, recursive=False):
        for child in self.children:
            if child._is_match(keyword, namespace):  # pylint: disable=protected-access
                yield child

            if recursive:
                for match in child.iterfind(
                    keyword, namespace=namespace, recursive=True
                ):
                    yield match

    def findall(self, keyword, namespace=None, recursive=False):
        return list(self.iterfind(keyword, namespace=namespace, recursive=recursive))

    def getparent(self):
        return self.parent

    def getroottree(self):
        parent = self
        while parent.parent is not None:
            parent = parent.parent
        return parent


def _change_all_whitespace_to_spaces(string):
    return re.sub(r"\s+", " ", string).strip()


class ModuleElement(YinElement):
    pass


class DefinitionElement(YinElement):
    @property
    def status(self):
        return _get_status(self)


class DataDefinitionElement(DefinitionElement):
    @property
    def is_config(self):
        for node in self.iter_parents(include_self=True):
            config_node = node.find("config", namespace=_YIN)
            if config_node and config_node["value"] == "false":
                return False

        return True

    @property
    def when_elements(self):
        return self.findall("when", namespace=_YIN)


class ContainerElement(DataDefinitionElement):
    @property
    def presence(self):
        return _get_subelem_attribute_or_default(self, "presence", "value")


def _get_subelem_attribute_or_default(
    data_def_element, subelem_name, attr_name, default=None, namespace=_YIN
):
    sub_elem = data_def_element.find(subelem_name, namespace=namespace)
    return sub_elem.get(attr_name, default) if sub_elem is not None else default


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
        return (
            (self.getparent() is not None)
            and (self.getparent().keyword == "list")
            and ((self.name, self.namespace) in self.getparent().key_ids)
        )


def _get_type(element):
    return element.find("type", namespace=_YIN)


def _get_status(element):
    return _get_subelem_attribute_or_default(
        element, "status", "value", default="current"
    )


def _get_default(element):
    return _get_subelem_attribute_or_default(element, "default", "value")


def _get_units(element):
    return _get_subelem_attribute_or_default(element, "units", "name")


def _is_mandatory(element):
    mandatory_string = _get_subelem_attribute_or_default(
        element, "mandatory", "value", default="false"
    )
    return mandatory_string == "true"


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
        data_def_element, "min-elements", "value", default="0"
    )
    return int(min_elements_string)


def _get_max_elements(data_def_element):
    max_elements_string = _get_subelem_attribute_or_default(
        data_def_element, "max-elements", "value", default="unbounded"
    )
    return None if max_elements_string == "unbounded" else int(max_elements_string)


def _get_ordered_by(data_def_element):
    return _get_subelem_attribute_or_default(
        data_def_element, "ordered-by", "value", default="system"
    )


class ListElement(DataDefinitionElement):
    @property
    def key_ids(self):
        keys = []

        key_string = _get_subelem_attribute_or_default(self, "key", "value", default="")
        for key_identifier in key_string.split():
            if ":" in key_identifier:
                prefix, name = key_identifier.split(":")
                namespace = self.nsmap[prefix]
            else:
                name = key_identifier
                namespace = self.namespace

            keys.append((name, namespace))

        return keys

    @property
    def unique(self):
        unique_str = _get_subelem_attribute_or_default(self, "unique", "tag", "")
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
    def unprefixed_name(self):
        return self.name.split(":")[-1]

    @property
    def prefix(self):
        if ":" in self.name:
            return self.name.split(":")[0]

        return super(TypeElement, self).prefix

    @property
    def base_type(self):
        typedef_elem = self.typedef
        return self if typedef_elem is None else typedef_elem.type.base_type

    @property
    def typedef(self):
        return self.find("typedef", namespace=_YIN)

    @property
    def bits(self):
        return self.base_type.findall("bit", namespace=_YIN)

    @property
    def enums(self):
        return self.base_type.findall("enum", namespace=_YIN)

    @property
    def fraction_digits(self):
        return _get_subelem_attribute_or_default(
            self.base_type, "fraction-digits", "value"
        )

    @property
    def length(self):
        range_value = _get_subelem_attribute_or_default(self, "length", "value")

        if range_value is None and self.typedef is not None:
            range_value = self.typedef.type.length

        return range_value

    @property
    def path(self):
        return _get_subelem_attribute_or_default(self.base_type, "path", "value")

    @property
    def patterns(self):
        return self.base_type.findall("pattern", namespace=_YIN)

    @property
    def range(self):
        range_value = _get_subelem_attribute_or_default(self, "range", "value")

        if range_value is None and self.typedef is not None:
            range_value = self.typedef.type.range

        return range_value

    @property
    def referenced_type(self):
        base_type_elem = self.base_type
        return (
            base_type_elem.find("type", namespace=_YIN)
            if base_type_elem.name == "leafref"
            else None
        )

    @property
    def subtypes(self):
        base_type_elem = self.base_type
        return (
            base_type_elem.findall("type", namespace=_YIN)
            if base_type_elem.name == "union"
            else []
        )

    @property
    def base_identity(self):
        return _get_subelem_attribute_or_default(self.base_type, "base", "name")

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
            identity, data_node.namespace_map, data_node.namespace
        )

        for identity_elem in root.iterfind("identity", namespace=_YIN):
            identifier = (identity_elem.name, identity_elem.namespace)
            if identifier == identifier_to_find:
                return identity_elem

        raise _error.MissingIdentityError(*identifier_to_find)


def _parse_identifier(identifier, nsmap, default_namespace):
    if ":" in identifier:
        prefix, name = identifier.split(":")
        namespace = nsmap[prefix]
    else:
        name = identifier
        namespace = default_namespace

    return name, namespace


class TypedefElement(YinElement):
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
    def position(self):
        position = _get_subelem_attribute_or_default(self, "position", "value")
        return int(position) if position is not None else None


class EnumElement(YinElement):
    @property
    def value(self):
        value = _get_subelem_attribute_or_default(self, "value", "value")
        return int(value) if value is not None else None


class PatternElement(YinElement):
    @property
    def value(self):
        return self.get("value")

    @property
    def error_message(self):
        return _get_subelem_attribute_or_default(self, "error-message", "value")


class WhenElement(YinElement):
    @property
    def condition(self):
        data_def_element = self.getparent()
        assert hasattr(
            data_def_element, "prefix"
        ), "Parent of 'when' element is not a data definition element"

        prefix = data_def_element.prefix
        return _ensure_xpath_names_prefixed(self.get("condition"), prefix)

    @property
    def context_node_is_parent(self):
        return self.get("context-node") == "parent"


def _ensure_xpath_names_prefixed(expression, prefix):
    tokens = xpathparser.tokens(expression)
    new_tokens = []

    for token_type, token in tokens:
        if token_type == "name" and ":" not in token:
            new_tokens.append("{}:{}".format(prefix, token))
        else:
            new_tokens.append(token)

    return "".join(new_tokens)


class IdentityElement(YinElement):
    @property
    def base(self):
        base = _get_subelem_attribute_or_default(self, "base", "name")

        if base is None:
            name = None
            namespace = None
        else:
            name, namespace = _parse_identifier(
                base, self.namespace_map, self.namespace
            )

        return name, namespace

    def get_derived_identities(self):
        return list(self.iterate_derived_identities())

    def iterate_derived_identities(self):
        for identity_elem in self.iterate_directly_derived_identities():
            yield identity_elem
            for nested_identity in identity_elem.iterate_derived_identities():
                yield nested_identity

    def get_directly_derived_identities(self):
        return list(self.iterate_directly_derived_identities())

    def iterate_directly_derived_identities(self):
        root = self.getroottree()
        for identity_elem in root.iterfind("identity", namespace=_YIN):
            if identity_elem.base == (self.name, self.namespace):
                yield identity_elem
