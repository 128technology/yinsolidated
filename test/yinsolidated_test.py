###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""Unit tests for the yinsolidated module"""

import os
import unittest

import yinsolidated


_NSMAP = {'yin': 'urn:ietf:params:xml:ns:yang:yin:1'}
_TEST_CONSOLIDATED_MODEL = os.path.join(os.path.dirname(__file__), 'model.xml')


class ParseConsolidatedModelFileTestCase(unittest.TestCase):

    def test_parse(self):
        model_tree = yinsolidated.parse(_TEST_CONSOLIDATED_MODEL)
        module_element = model_tree.getroot()
        container_element = module_element.find(
            'yin:container[@name="test"]', namespaces=_NSMAP)
        self.assertEqual('test', container_element.name)


class YinElementTestCase(unittest.TestCase):

    def test_keyword(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual('module', module_elem.keyword)

    def test_namespace_map(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:a="alpha"
                    xmlns:b="bravo"/>
            """)

        self.assertEqual({'a': 'alpha', 'b': 'bravo'},
                         module_elem.namespace_map)

    def test_description(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <description>
                    <text>
                        This is a long description of the data model that wraps
                        onto the next line
                    </text>
                </description>
            </module>
            """)

        self.assertEqual('This is a long description of the data model that '
                         'wraps onto the next line', module_elem.description)

    def test_no_description(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(module_elem.description)

    def test_child_data_definitions(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <namespace uri="test:ns"/>
                <prefix value="t"/>
                <container/>
                <leaf/>
                <leaf-list/>
                <list/>
                <choice/>
                <case/>
                <anyxml/>
            </module>
            """)

        self.assertEqual(7, len(list(module_elem.iterate_data_definitions())))


class DefinitionElementTestCase(unittest.TestCase):

    def test_name(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system"
                    xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual('system', choice_elem.name)

    def test_namespace_from_module(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:test="test:ns"
                    module-prefix="test">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        self.assertEqual('test:ns', choice_elem.namespace)

    def test_namespace_from_augmenting_node(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:out="outer:ns"
                    module-prefix="out">
                <container name="test-container"
                           xmlns:in="inner:ns"
                           module-prefix="in">
                    <choice/>
                </container>
            </module>
            """)
        choice_elem = module_elem.find('.//yin:choice', namespaces=_NSMAP)

        self.assertEqual('inner:ns', choice_elem.namespace)

    def test_prefix_from_module(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    module-prefix="test">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        self.assertEqual('test', choice_elem.prefix)

    def test_prefix_from_augmenting_node(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    module-prefix="outer">
                <container name="test-container"
                           module-prefix="inner">
                    <choice/>
                </container>
            </module>
            """)
        choice_elem = module_elem.find('.//yin:choice', namespaces=_NSMAP)

        self.assertEqual('inner', choice_elem.prefix)

    def test_missing_prefix(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        with self.assertRaises(yinsolidated.MissingPrefixError):
            choice_elem.prefix

    def test_status(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system" xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <status value='obsolete'/>
            </choice>
            """)

        self.assertEqual('obsolete', choice_elem.status)

    def test_default_status(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system" xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual('current', choice_elem.status)


class RpcElementTestCase(unittest.TestCase):

    def test_input(self):
        rpc_elem = yinsolidated.fromstring("""
            <rpc xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <input/>
            </rpc>
            """)

        self.assertIsNotNone(rpc_elem.input)

    def test_output(self):
        rpc_elem = yinsolidated.fromstring("""
            <rpc xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <output/>
            </rpc>
            """)

        self.assertIsNotNone(rpc_elem.output)


class DataDefinitionElementTestCase(unittest.TestCase):

    def test_is_config_false(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <config value="false"/>
            </choice>
            """)

        self.assertFalse(choice_elem.is_config)

    def test_is_config_no_parent(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertTrue(choice_elem.is_config)

    def test_is_config_parent_false(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <config value="false"/>
                <leaf/>
            </choice>
            """)
        leaf_elem = choice_elem[1]

        self.assertFalse(leaf_elem.is_config)

    def test_when_elements(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <when condition="false"/>
                <when condition="true"/>
            </container>
            """)

        self.assertEqual(2, len(container_elem.when_elements))


class ContainerElementTestCase(unittest.TestCase):

    def test_presence(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <presence value="My existence is meaningful"/>
            </container>
            """)

        self.assertEqual('My existence is meaningful', container_elem.presence)

    def test_no_presence(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(container_elem.presence)


class LeafElementTestCase(unittest.TestCase):

    def test_type(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <type name="uint8"/>
            </leaf>
            """)

        self.assertEqual('uint8', leaf_elem.type.base_type.name)

    def test_default(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <default value="600"/>
            </leaf>
            """)

        self.assertEqual('600', leaf_elem.default)

    def test_no_default(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(leaf_elem.default)

    def test_units(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <units name="seconds"/>
            </leaf>
            """)

        self.assertEqual('seconds', leaf_elem.units)

    def test_no_units(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(leaf_elem.units)

    def test_is_mandatory(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="true"/>
            </leaf>
            """)

        self.assertTrue(leaf_elem.is_mandatory)

    def test_not_mandatory(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="false"/>
            </leaf>
            """)

        self.assertFalse(leaf_elem.is_mandatory)

    def test_not_mandatory_implicit(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertFalse(leaf_elem.is_mandatory)

    def test_is_list_key(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  xmlns:test="test:ns"
                  module-prefix="test">
                <key value="alpha"/>
                <leaf name="alpha"/>
            </list>
            """)
        leaf_elem = list_elem.find('yin:leaf', namespaces=_NSMAP)

        self.assertTrue(leaf_elem.is_list_key)

    def test_list_child_not_key(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  xmlns:test="test:ns"
                  module-prefix="test">
                <key value="alpha"/>
                <leaf name="bravo"/>
            </list>
            """)
        leaf_elem = list_elem.find('yin:leaf', namespaces=_NSMAP)

        self.assertFalse(leaf_elem.is_list_key)

    def test_non_list_child_not_key(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertFalse(leaf_elem.is_list_key)


class LeafListElementTestCase(unittest.TestCase):

    def test_type(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <type name="uint8"/>
            </leaf-list>
            """)

        self.assertEqual('uint8', leaf_list_elem.type.base_type.name)

    def test_units(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <units name="seconds"/>
            </leaf-list>
            """)

        self.assertEqual('seconds', leaf_list_elem.units)

    def test_no_units(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(leaf_list_elem.units)

    def test_min_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <min-elements value="10"/>
            </leaf-list>
            """)

        self.assertEqual(10, leaf_list_elem.min_elements)

    def test_no_min_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual(0, leaf_list_elem.min_elements)

    def test_max_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <max-elements value="10"/>
            </leaf-list>
            """)

        self.assertEqual(10, leaf_list_elem.max_elements)

    def test_no_max_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(leaf_list_elem.max_elements)

    def test_ordered_by_user(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <ordered-by value="user"/>
            </leaf-list>
            """)

        self.assertEqual('user', leaf_list_elem.ordered_by)

    def test_no_ordered_by(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual('system', leaf_list_elem.ordered_by)


class ListElementTestCase(unittest.TestCase):

    def test_keys(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:a="alpha:ns"
                    xmlns:b="bravo:ns"
                    xmlns:c="charlie:ns"
                    module-prefix="c">
                <list>
                    <key value="a:alpha b:bravo charlie"/>
                </list>
            </module>
            """)
        list_elem = module_elem.find('yin:list', namespaces=_NSMAP)

        self.assertEqual([
            ('alpha', 'alpha:ns'),
            ('bravo', 'bravo:ns'),
            ('charlie', 'charlie:ns')
        ], list_elem.key_ids)

    def test_no_keys(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual([], list_elem.key_ids)

    def test_unique(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <unique tag="alpha bravo charlie"/>
            </list>
            """)

        self.assertEqual(['alpha', 'bravo', 'charlie'], list_elem.unique)

    def test_min_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <min-elements value="10"/>
            </list>
            """)

        self.assertEqual(10, list_elem.min_elements)

    def test_no_min_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual(0, list_elem.min_elements)

    def test_max_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <max-elements value="10"/>
            </list>
            """)

        self.assertEqual(10, list_elem.max_elements)

    def test_no_max_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(list_elem.max_elements)

    def test_ordered_by_user(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <ordered-by value="user"/>
            </list>
            """)

        self.assertEqual('user', list_elem.ordered_by)

    def test_no_ordered_by(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertEqual('system', list_elem.ordered_by)


class AnyxmlElementTestCase(unittest.TestCase):

    def test_is_mandatory(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="true"/>
            </anyxml>
            """)

        self.assertTrue(anyxml_elem.is_mandatory)

    def test_not_mandatory(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="false"/>
            </anyxml>
            """)

        self.assertFalse(anyxml_elem.is_mandatory)

    def test_not_mandatory_implicit(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertFalse(anyxml_elem.is_mandatory)


class TypeElementTestCase(unittest.TestCase):

    def test_name(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="counter">
                <typedef name="counter">
                    <type name="uint32"/>
                </typedef>
            </type>
            """)

        self.assertEqual('counter', type_elem.name)

    def test_base(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="counter">
                <typedef name="percentage">
                    <type name="meter">
                        <typedef name="meter">
                            <type name="uint8"/>
                        </typedef>
                    </type>
                    <range value="0..100"/>
                </typedef>
            </type>
            """)

        self.assertEqual('uint8', type_elem.base_type.name)

    def test_base_for_leafref(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="test-leafref">
                <typedef name="test-leafref">
                    <type name="leafref">
                        <type name="uint32"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('leafref', type_elem.base_type.name)

    def test_base_for_union(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="test-union">
                <typedef name="test-union">
                    <type name="union">
                        <type name="uint32"/>
                        <type name="string"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('union', type_elem.base_type.name)

    def test_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="counter">
                <typedef name="counter">
                    <type name="uint32"/>
                </typedef>
            </type>
            """)

        self.assertIsNotNone(type_elem.typedef)

    def test_no_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint32"/>
            """)

        self.assertIsNone(type_elem.typedef)

    def test_bits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="bits">
                <bit name="alpha"/>
                <bit name="bravo"/>
            </type>
            """)

        bit_names = [bit.name for bit in type_elem.bits]
        self.assertEqual(['alpha', 'bravo'], bit_names)

    def test_bits_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="bits">
                        <bit name="alpha"/>
                        <bit name="bravo"/>
                    </type>
                </typedef>
            </type>
            """)

        bit_names = [bit.name for bit in type_elem.bits]
        self.assertEqual(['alpha', 'bravo'], bit_names)

    def test_enums(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="enumeration">
                <enum name="alpha"/>
                <enum name="bravo"/>
            </type>
            """)

        enum_names = [enum.name for enum in type_elem.enums]
        self.assertEqual(['alpha', 'bravo'], enum_names)

    def test_enums_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="enumeration">
                        <enum name="alpha"/>
                        <enum name="bravo"/>
                    </type>
                </typedef>
            </type>
            """)

        enum_names = [enum.name for enum in type_elem.enums]
        self.assertEqual(['alpha', 'bravo'], enum_names)

    def test_fraction_digits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="decimal64">
                <fraction-digits value="2"/>
            </type>
            """)

        self.assertEqual('2', type_elem.fraction_digits)

    def test_fraction_digits_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="decimal64">
                        <fraction-digits value="2"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('2', type_elem.fraction_digits)

    def test_no_fraction_digits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
            </type>
            """)

        self.assertIsNone(type_elem.fraction_digits)

    def test_base_identity(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="identityref">
                <base name="base-identity"/>
            </type>
            """)

        self.assertEqual('base-identity', type_elem.base_identity)

    def test_base_identity_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="identityref">
                        <base name="base-identity"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('base-identity', type_elem.base_identity)

    def test_identities_base_in_same_namespace(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:t="test:ns"
                    module-prefix="t">
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="base-identity"/>
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="derived-identity">
                    <base name="base-identity"/>
                </identity>
                <identity xmlns:o="other:ns"
                          module-prefix="o"
                          name="another-base-identity"/>
                <identity xmlns:t="test:ns"
                          xmlns:o="other:ns"
                          module-prefix="t"
                          name="another-derived-identity">
                    <base name="o:another-base-identity"/>
                </identity>
                <leaf name="test-leaf">
                    <type name="identityref">
                        <base name="base-identity"/>
                    </type>
                </leaf>
            </module>
            """)
        type_elem = module_elem.find('yin:leaf/yin:type', namespaces=_NSMAP)

        identities = type_elem.get_identities()

        self.assertEqual(1, len(identities))
        self.assertEqual('derived-identity', identities[0].name)

    def test_identities_base_in_different_namespace(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:t="test:ns"
                    module-prefix="t">
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="base-identity"/>
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="derived-identity">
                    <base name="base-identity"/>
                </identity>
                <identity xmlns:o="other:ns"
                          module-prefix="o"
                          name="another-base-identity"/>
                <identity xmlns:t="test:ns"
                          xmlns:o="other:ns"
                          module-prefix="t"
                          name="another-derived-identity">
                    <base name="o:another-base-identity"/>
                </identity>
                <leaf name="test-leaf"
                      xmlns:o="other:ns">
                    <type name="identityref">
                        <base name="o:another-base-identity"/>
                    </type>
                </leaf>
            </module>
            """)
        type_elem = module_elem.find('yin:leaf/yin:type', namespaces=_NSMAP)

        identities = type_elem.get_identities()

        self.assertEqual(1, len(identities))
        self.assertEqual('another-derived-identity', identities[0].name)

    def test_missing_identity(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:t="test:ns"
                    module-prefix="t">
                <leaf name="test-leaf"
                      xmlns:o="other:ns">
                    <type name="identityref">
                        <base name="t:base-identity"/>
                    </type>
                </leaf>
            </module>
            """)
        type_elem = module_elem.find('yin:leaf/yin:type', namespaces=_NSMAP)

        with self.assertRaises(yinsolidated.MissingIdentityError):
            type_elem.get_identities()

    def test_no_identities(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
            </type>
            """)

        self.assertEqual(0, len(type_elem.get_identities()))

    def test_length(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
                <length value="1..253"/>
            </type>
            """)

        self.assertEqual('1..253', type_elem.length)

    def test_length_typedefs(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="string">
                        <length value="1..253"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('1..253', type_elem.length)

        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="indirected-fake-type">
                    <type name="another-fake-type">
                        <typedef name="fake-type">
                            <type name="string"/>
                        </typedef>
                        <length value="8..110"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('8..110', type_elem.length)

        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="string">
                        <length value="1..17"/>
                    </type>
                </typedef>
                <length value="9..17"/>
            </type>
            """)

        self.assertEqual('9..17', type_elem.length)

    def test_no_length(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1" name="string"/>
            """)

        self.assertIsNone(type_elem.length)

    def test_path(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <path value="/a/fake/path"/>
            </type>
            """)

        self.assertEqual('/a/fake/path', type_elem.path)

    def test_path_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="leafref">
                        <path value="/a/fake/path"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('/a/fake/path', type_elem.path)

    def test_no_path(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1" name="string"/>
            """)

        self.assertIsNone(type_elem.path)

    def test_patterns(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
                <pattern value="[a-zA-Z0-9_\\-]*">
                    <error-message>
                      <value>Must be alphanumeric</value>
                    </error-message>
                </pattern>
                <pattern value=".*"/>
            </type>
            """)

        self.assertEqual(2, len(type_elem.patterns))

        self.assertEqual(r'[a-zA-Z0-9_\-]*', type_elem.patterns[0].value)
        self.assertEqual('Must be alphanumeric',
                         type_elem.patterns[0].error_message)

        self.assertEqual('.*', type_elem.patterns[1].value)
        self.assertIsNone(type_elem.patterns[1].error_message)

    def test_patterns_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="string">
                        <pattern value="[a-zA-Z0-9_\\-]*">
                            <error-message>
                              <value>Must be alphanumeric</value>
                            </error-message>
                        </pattern>
                        <pattern value=".*"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual(2, len(type_elem.patterns))

        self.assertEqual(r'[a-zA-Z0-9_\-]*', type_elem.patterns[0].value)
        self.assertEqual('Must be alphanumeric',
                         type_elem.patterns[0].error_message)

        self.assertEqual('.*', type_elem.patterns[1].value)
        self.assertIsNone(type_elem.patterns[1].error_message)

    def test_range(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint8">
                <range value="1..253"/>
            </type>
            """)

        self.assertEqual('1..253', type_elem.range)

    def test_range_typedefs(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="uint8">
                        <range value="1..253"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('1..253', type_elem.range)

        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="another-fake-type">
                        <typedef name="indirected-fake-type">
                            <type name="uint8"/>
                        </typedef>
                        <range value="7..9"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('7..9', type_elem.range)

        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="uint8">
                        <range value="1..227"/>
                    </type>
                </typedef>
                <range value="4..128"/>
            </type>
            """)

        self.assertEqual('4..128', type_elem.range)

    def test_no_range(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint8"/>
            """)

        self.assertIsNone(type_elem.range)

    def test_referenced_type_for_leafref(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <type name="string"/>
            </type>
            """)

        self.assertEqual('string', type_elem.referenced_type.base_type.name)

    def test_referenced_type_for_union(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="union">
                <type name="uint8"/>
                <type name="string"/>
            </type>
            """)

        self.assertIsNone(type_elem.referenced_type)

    def test_referenced_type_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="leafref">
                        <type name="string"/>
                    </type>
                </typedef>
            </type>
            """)

        self.assertEqual('string', type_elem.referenced_type.base_type.name)

    def test_subtypes_for_union(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="union">
                <type name="uint8"/>
                <type name="string"/>
            </type>
            """)

        subtype_names = [elem.base_type.name for elem in type_elem.subtypes]
        self.assertEqual(['uint8', 'string'], subtype_names)

    def test_subtypes_for_leafref(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <type name="uint8"/>
            </type>
            """)

        self.assertEqual(0, len(type_elem.subtypes))

    def test_subtypes_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="fake-type">
                <typedef name="fake-type">
                    <type name="union">
                        <type name="uint8"/>
                        <type name="string"/>
                    </type>
                </typedef>
            </type>
            """)

        subtype_names = [elem.base_type.name for elem in type_elem.subtypes]
        self.assertEqual(['uint8', 'string'], subtype_names)


class TypedefElementTestCase(unittest.TestCase):

    def test_name(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
            </typedef>
            """)

        self.assertEqual('counter', typedef_elem.name)

    def test_type(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <type name="uint32"/>
            </typedef>
            """)

        self.assertEqual('uint32', typedef_elem.type.name)

    def test_default(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <default value="600"/>
            </typedef>
            """)

        self.assertEqual('600', typedef_elem.default)

    def test_no_default(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter"/>
            """)

        self.assertIsNone(typedef_elem.default)

    def test_units(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <units name="seconds"/>
            </typedef>
            """)

        self.assertEqual('seconds', typedef_elem.units)

    def test_no_units(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter"/>
            """)

        self.assertIsNone(typedef_elem.units)


class BitElementTestCase(unittest.TestCase):

    def test_name(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                 name="alpha"/>
            """)

        self.assertEqual('alpha', bit_elem.name)

    def test_position(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <position value="1"/>
            </bit>
            """)

        self.assertEqual(1, bit_elem.position)

    def test_no_position(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(bit_elem.position)


class EnumElementTestCase(unittest.TestCase):

    def test_name(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="alpha"/>
            """)

        self.assertEqual('alpha', enum_elem.name)

    def test_value(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <value value="1"/>
            </enum>
            """)

        self.assertEqual(1, enum_elem.value)

    def test_no_value(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertIsNone(enum_elem.value)


class WhenElementTestCase(unittest.TestCase):

    def test_no_prefix_added(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                       xmlns:t="test:ns"
                       module-prefix="t">
                <when condition="t:foo = 'bar'"/>
            </container>
            """)
        when_element = container_elem.find('yin:when', namespaces=_NSMAP)

        self.assertEqual("t:foo = 'bar'", when_element.condition)
        self.assertEqual({'t': 'test:ns'}, when_element.namespace_map)

    def test_prefix_added(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                       xmlns:d="default:ns"
                       xmlns:t="test:ns"
                       module-prefix="d">
                <when condition="../foo/bar = 'alpha' | /t:root/test = 'bravo'"/>
            </container>
            """)  # nopep8

        when_element = container_elem.find('yin:when', namespaces=_NSMAP)

        self.assertEqual("../d:foo/d:bar = 'alpha' | /t:root/d:test = 'bravo'",
                         when_element.condition)
        self.assertEqual({'d': 'default:ns', 't': 'test:ns'},
                         when_element.namespace_map)

    def test_self_context(self):
        when_element = yinsolidated.fromstring("""
            <when xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        self.assertFalse(when_element.context_node_is_parent)

    def test_parent_context(self):
        when_element = yinsolidated.fromstring("""
            <when xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  context-node="parent"/>
            """)

        self.assertTrue(when_element.context_node_is_parent)


class IdentityElementTestCase(unittest.TestCase):

    def test_name(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      name="test-identity"/>
            """)

        self.assertEqual('test-identity', identity_elem.name)

    def test_namespace(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity"/>
            """)

        self.assertEqual('test:ns', identity_elem.namespace)

    def test_prefix(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity"/>
            """)

        self.assertEqual('t', identity_elem.prefix)

    def test_no_base(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      name="test-identity"/>
            """)

        self.assertEqual((None, None), identity_elem.base)

    def test_base_in_same_namespace(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity">
                <base name="base-identity"/>
            </identity>
            """)

        self.assertEqual(('base-identity', 'test:ns'), identity_elem.base)

    def test_base_in_different_namespace(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      xmlns:o="other:ns"
                      module-prefix="t"
                      name="test-identity">
                <base name="o:base-identity"/>
            </identity>
            """)

        self.assertEqual(('base-identity', 'other:ns'), identity_elem.base)

    def test_iterate_derived_identities(self):
        module_element = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="base-identity">
                </identity>
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="derived-identity-1">
                    <base name="base-identity"/>
                </identity>
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="another-base-identity">
                </identity>
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="derived-identity-2">
                    <base name="another-base-identity"/>
                </identity>
                <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                          xmlns:o="other:ns"
                          xmlns:t="test:ns"
                          module-prefix="o"
                          name="external-derived-identity">
                    <base name="t:base-identity"/>
                </identity>
            </module>
            """)
        base_identity = module_element.find('yin:identity', namespaces=_NSMAP)
        self.assertEqual('base-identity', base_identity.name)

        derived_identities = base_identity.get_derived_identities()

        self.assertEqual(2, len(derived_identities))
        self.assertEqual('derived-identity-1', derived_identities[0].name)
        self.assertEqual('external-derived-identity',
                         derived_identities[1].name)


if __name__ == '__main__':
    unittest.main()
