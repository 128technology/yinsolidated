###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""Unit tests for the consolidated_model pyang plugin"""

from __future__ import unicode_literals

import os
import unittest
import subprocess

import pyang
import xmlunittest
from lxml import etree

from yinsolidated.plugin import plugin


YINSOLIDATED_PLUGIN_DIRECTORY = os.path.dirname(plugin.__file__)

YIN_NAMESPACE = 'urn:ietf:params:xml:ns:yang:yin:1'
TEST_NAMESPACE = 'urn:xml:ns:test'
AUGMENTING_NAMESPACE = 'urn:xml:ns:test:augment'
NSMAP = {
    'yin': YIN_NAMESPACE,
    'test': TEST_NAMESPACE,
    'aug': AUGMENTING_NAMESPACE
}

TEST_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
MODULES_DIR = os.path.join(TEST_FILE_DIR, 'modules')

MAIN_MODULE = os.path.join(MODULES_DIR, 'test-module.yang')
AUGMENTING_MODULE = os.path.join(MODULES_DIR, 'augmenting-module.yang')

EXPECTED_MODEL_PATH = os.path.join(TEST_FILE_DIR,
                                   'expected_consolidated_model.xml')

PYANG_COMMAND = [
    'pyang',
    '-f', 'yinsolidated',
    '-p', MODULES_DIR,
]

if pyang.__version__ < '1.7.2':
    PYANG_COMMAND.extend(['--plugindir', YINSOLIDATED_PLUGIN_DIRECTORY])

PYANG_COMMAND.extend([MAIN_MODULE, AUGMENTING_MODULE])

CONSOLIDATED_MODEL_XML = subprocess.check_output(PYANG_COMMAND)

CONSOLIDATED_MODEL = etree.fromstring(CONSOLIDATED_MODEL_XML)


class ModuleTestCase(xmlunittest.XmlTestCase):

    def test_module_root_element(self):
        qname = etree.QName(CONSOLIDATED_MODEL.tag)
        self.assertEqual('module', qname.localname)
        self.assertEqual(YIN_NAMESPACE, qname.namespace)

    def test_prefix_attribute(self):
        prefix = CONSOLIDATED_MODEL.get('module-prefix')
        self.assertEqual('test', prefix)

    def test_nsmap(self):
        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE
        }
        self.assertEqual(expected_nsmap, CONSOLIDATED_MODEL.nsmap)

    def test_yang_version(self):
        yang_version = CONSOLIDATED_MODEL.xpath(
            'yin:yang-version/@value', namespaces=NSMAP)[0]
        self.assertEqual('1', yang_version)

    def test_namespace(self):
        namespace = CONSOLIDATED_MODEL.xpath(
            'yin:namespace/@uri', namespaces=NSMAP)[0]
        self.assertEqual(TEST_NAMESPACE, namespace)

    def test_prefix(self):
        prefix = CONSOLIDATED_MODEL.xpath(
            'yin:prefix/@value', namespaces=NSMAP)[0]
        self.assertEqual('test', prefix)

    def test_organization(self):
        organization_elem = CONSOLIDATED_MODEL.find(
            'yin:organization', namespaces=NSMAP)
        actual_xml = etree.tostring(organization_elem)

        expected_xml = """
            <organization xmlns="{yin}">
                <text>None</text>
            </organization>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_contact(self):
        contact_elem = CONSOLIDATED_MODEL.find(
            'yin:contact', namespaces=NSMAP)
        actual_xml = etree.tostring(contact_elem)

        expected_xml = """
            <contact xmlns="{yin}">
                <text>Somebody</text>
            </contact>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_description(self):
        description_elem = CONSOLIDATED_MODEL.find(
            'yin:description', namespaces=NSMAP)
        actual_xml = etree.tostring(description_elem)

        expected_xml = """
            <description xmlns="{yin}">
                <text>Test module containing an exhaustive set of possible YANG statements</text>
            </description>
            """.format(**NSMAP)  # nopep8

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_revision(self):
        revision_elem = CONSOLIDATED_MODEL.find(
            'yin:revision', namespaces=NSMAP)
        actual_xml = etree.tostring(revision_elem)

        expected_xml = """
            <revision xmlns="{yin}" date="2016-04-22">
                <description>
                    <text>Initial revision</text>
                </description>
            </revision>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_extension_definition(self):
        extension_elem = CONSOLIDATED_MODEL.find(
            'yin:extension[@name="test-extension"]', namespaces=NSMAP)

        actual_xml = etree.tostring(extension_elem)

        expected_xml = """
            <extension xmlns="{yin}" name="test-extension">
                <argument name="test-argument">
                    <yin-element value="false"/>
                </argument>
                <description>
                    <text>A test extension</text>
                </description>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
            </extension>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_another_extension_definition(self):
        another_extension_elem = CONSOLIDATED_MODEL.find(
            'yin:extension[@name="another-test-extension"]', namespaces=NSMAP)

        actual_xml = etree.tostring(another_extension_elem)

        expected_xml = """
            <extension xmlns="{yin}" name="another-test-extension">
                <argument name="another-test-argument">
                    <yin-element value="true"/>
                </argument>
            </extension>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_test_extension(self):
        test_extension_text = CONSOLIDATED_MODEL.findtext(
            'test:test-extension', namespaces=NSMAP)
        self.assertEqual('test-value', test_extension_text)

    def test_another_test_extension(self):
        another_test_extension_text = CONSOLIDATED_MODEL.findtext(
            'test:another-test-extension', namespaces=NSMAP)
        self.assertEqual('another-test-value', another_test_extension_text)

    def test_feature(self):
        feature_elem = CONSOLIDATED_MODEL.find(
            'yin:feature', namespaces=NSMAP)
        actual_xml = etree.tostring(feature_elem)

        expected_xml = """
            <feature xmlns="{yin}" name="test-feature">
                <description>
                    <text>A test feature</text>
                </description>
            </feature>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_base_identity(self):
        base_identity_elem = CONSOLIDATED_MODEL.find(
            'yin:identity[@name="test-base-identity"]', namespaces=NSMAP)
        actual_xml = etree.tostring(base_identity_elem)

        expected_xml = """
            <identity xmlns="{yin}"
                      xmlns:test="{test}"
                      module-prefix="test"
                      name="test-base-identity">
                <description>
                    <text>A base identity</text>
                </description>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
            </identity>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_identity_from_augmenting_module(self):
        augmenting_identity_elem = CONSOLIDATED_MODEL.find(
            'yin:identity[@name="augmenting-derived-identity"]',
            namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_identity_elem)

        expected_xml = """
            <identity xmlns="{yin}"
                      xmlns:t="{test}"
                      xmlns:aug="{aug}"
                      module-prefix="aug"
                      name="augmenting-derived-identity">
                <description>
                    <text>A derived identity in an augmenting module</text>
                </description>
                <base name="t:test-base-identity"/>
            </identity>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_no_typedefs_added(self):
        typedef_elems = CONSOLIDATED_MODEL.findall(
            'yin:typedef', namespaces=NSMAP)
        self.assertEqual(0, len(typedef_elems))


class SubmoduleTestCase(unittest.TestCase):

    def test_data_definitions_included(self):
        submodule_container_elems = CONSOLIDATED_MODEL.findall(
            'yin:container[@name="submodule-container"]', namespaces=NSMAP)
        self.assertEqual(1, len(submodule_container_elems))


class ChoiceTestCase(xmlunittest.XmlTestCase):

    def test_choice(self):
        choice_elem = CONSOLIDATED_MODEL.find(
            'yin:choice[@name="root-choice"]', namespaces=NSMAP)
        actual_xml = etree.tostring(choice_elem)

        expected_xml = """
            <choice xmlns="{yin}" name="root-choice">
                <config value="true"/>
                <default value="test-case"/>
                <description>
                    <text>A choice at the model root</text>
                </description>
                <if-feature name="test-feature"/>
                <mandatory value="false"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="obsolete"/>
                <when condition="../root-leaf != 'nonsense'"/>
                <case name="anyxml-case">
                    <anyxml name="anyxml-case"/>
                </case>
                <case name="test-case">
                    <description>
                        <text>A test case</text>
                    </description>
                    <if-feature name="test-feature"/>
                    <reference>
                        <text>RFC 6020</text>
                    </reference>
                    <status value="current"/>
                    <when condition="../root-leaf != 'nonsense'"/>
                    <anyxml name="anyxml-within-case"/>
                    <choice name="choice-within-case"/>
                    <container name="container-within-case"/>
                    <leaf name="leaf-within-case">
                        <type name="string"/>
                    </leaf>
                    <leaf-list name="leaf-list-within-case">
                        <type name="string"/>
                    </leaf-list>
                    <list name="list-within-case">
                        <config value="false"/>
                    </list>
                    <anyxml name="grouped-anyxml"/>
                </case>
                <case name="container-case">
                    <container name="container-case"/>
                </case>
                <case name="leaf-case">
                    <leaf name="leaf-case">
                        <type name="string"/>
                    </leaf>
                </case>
                <case name="leaf-list-case">
                    <leaf-list name="leaf-list-case">
                        <type name="string"/>
                    </leaf-list>
                </case>
                <case name="list-case">
                    <list name="list-case">
                        <config value="false"/>
                    </list>
                </case>
                <case name="augmenting-case"
                      module-prefix="aug">
                    <leaf name="augmenting-case-leaf">
                        <type name="string"/>
                    </leaf>
                </case>
            </choice>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class ContainerTestCase(xmlunittest.XmlTestCase):

    def test_container(self):
        container_elem = CONSOLIDATED_MODEL.find(
            'yin:container[@name="root-container"]', namespaces=NSMAP)
        actual_xml = etree.tostring(container_elem)

        expected_xml = """
            <container xmlns="{yin}" name="root-container">
                <config value="true"/>
                <description>
                    <text>A container at the model root</text>
                </description>
                <if-feature name="test-feature"/>
                <must condition="test-leaf != 'nonsense'">
                    <error-message>
                        <value>test-leaf is nonsense</value>
                    </error-message>
                </must>
                <presence value="This container has presence"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <when condition="../root-leaf != 'nonsense'"/>
                <anyxml name="test-anyxml"/>
                <choice name="test-choice"/>
                <container name="test-nested-container"/>
                <leaf name="test-leaf">
                    <type name="inner-type">
                        <typedef name="inner-type">
                            <type name="string"/>
                        </typedef>
                    </type>
                </leaf>
                <leaf-list name="test-leaf-list">
                    <type name="string"/>
                </leaf-list>
                <list name="test-list">
                    <config value="false"/>
                </list>
                <leaf name="grouped-leaf">
                    <type name="string"/>
                </leaf>
            </container>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class LeafTestCase(xmlunittest.XmlTestCase):

    def test_leaf(self):
        leaf_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf[@name="root-leaf"]', namespaces=NSMAP)
        actual_xml = etree.tostring(leaf_elem)

        expected_xml = """
            <leaf xmlns="{yin}" name="root-leaf">
                <config value="true"/>
                <default value="test-default"/>
                <description>
                    <text>A leaf at the model root</text>
                </description>
                <if-feature name="test-feature"/>
                <mandatory value="false"/>
                <must condition="count(../root-leaf-list) &gt; 0"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <type name="string"/>
                <units name="goobers"/>
                <when condition="count(../root-leaf-list) &gt; 0"/>
            </leaf>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class LeafListTestCase(xmlunittest.XmlTestCase):

    def test_leaf_list(self):
        leaf_list_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf-list[@name="root-leaf-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(leaf_list_elem)

        expected_xml = """
            <leaf-list xmlns="{yin}" name="root-leaf-list">
                <config value="true"/>
                <description>
                    <text>A leaf-list at the model root</text>
                </description>
                <if-feature name="test-feature"/>
                <max-elements value="10"/>
                <min-elements value="1"/>
                <must condition="../root-leaf != 'nonsense'"/>
                <ordered-by value="user"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <type name="string"/>
                <units name="awesomeness"/>
                <when condition="../root-leaf != 'nonsense'"/>
            </leaf-list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class ListTestCase(xmlunittest.XmlTestCase):

    def test_list(self):
        list_elem = CONSOLIDATED_MODEL.find(
            'yin:list[@name="root-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(list_elem)

        expected_xml = """
            <list xmlns="{yin}" name="root-list">
                <config value="true"/>
                <description>
                    <text>A list at the model root</text>
                </description>
                <if-feature name="test-feature"/>
                <key value="test-key"/>
                <max-elements value="100"/>
                <min-elements value="50"/>
                <must condition="../root-leaf != 'nonsense'"/>
                <ordered-by value="system"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <unique tag="grouped-leaf"/>
                <when condition="../root-leaf != 'nonsense'"/>
                <anyxml name="test-anyxml"/>
                <choice name="test-choice"/>
                <container name="test-container"/>
                <leaf name="test-key">
                    <type name="inner-type">
                        <typedef name="inner-type">
                            <type name="string"/>
                        </typedef>
                    </type>
                </leaf>
                <leaf-list name="test-leaf-list">
                    <type name="string"/>
                </leaf-list>
                <list name="test-nested-list">
                    <config value="false"/>
                </list>
                <leaf name="grouped-leaf">
                    <type name="string"/>
                </leaf>
            </list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class UsesTestCase(xmlunittest.XmlTestCase):

    def test_grouped_choice(self):
        grouped_choice_elem = CONSOLIDATED_MODEL.find(
            'yin:choice[@name="grouped-choice"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_choice_elem)

        expected_xml = """
            <choice xmlns="{yin}" name="grouped-choice">
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
            </choice>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_grouped_container(self):
        grouped_container_elem = CONSOLIDATED_MODEL.find(
            'yin:container[@name="grouped-container"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_container_elem)

        expected_xml = """
            <container xmlns="{yin}" name="grouped-container">
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
                <anyxml name="augmented-in-uses-anyxml">
                    <when condition="../grouped-leaf != 'nonsense'"
                          context-node="parent"/>
                </anyxml>
            </container>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_grouped_leaf(self):
        grouped_leaf_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf[@name="grouped-leaf"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_leaf_elem)

        expected_xml = """
            <leaf xmlns="{yin}" name="grouped-leaf">
                <type name="grouped-typedef">
                    <typedef name="grouped-typedef">
                        <type name="string"/>
                    </typedef>
                </type>
                <description>
                    <text>A leaf in a grouping with a refined description</text>
                </description>
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
            </leaf>
            """.format(**NSMAP)  # nopep8

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_grouped_leaf_list(self):
        grouped_leaf_list_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf-list[@name="grouped-leaf-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_leaf_list_elem)

        expected_xml = """
            <leaf-list xmlns="{yin}" name="grouped-leaf-list">
                <type name="string"/>
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
            </leaf-list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_grouped_list(self):
        grouped_list_elem = CONSOLIDATED_MODEL.find(
            'yin:list[@name="grouped-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_list_elem)

        expected_xml = """
            <list xmlns="{yin}" name="grouped-list">
                <config value="false"/>
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
            </list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

    def test_nested_uses(self):
        nested_grouped_anyxml_elem = CONSOLIDATED_MODEL.find(
            'yin:anyxml[@name="nested-grouped-anyxml"]', namespaces=NSMAP)
        actual_xml = etree.tostring(nested_grouped_anyxml_elem)

        expected_xml = """
            <anyxml xmlns="{yin}" name="nested-grouped-anyxml">
                <if-feature name="test-feature"/>
                <when condition="../root-leaf != 'nonsense'"
                      context-node="parent"/>
                <when condition="grouped-leaf != 'nonsense'"
                      context-node="parent"/>
            </anyxml>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class NotificationTestCase(xmlunittest.XmlTestCase):

    def test_notification(self):
        notification_elem = CONSOLIDATED_MODEL.find(
            'yin:notification[@name="test-notification"]', namespaces=NSMAP)
        actual_xml = etree.tostring(notification_elem)

        expected_xml = """
            <notification xmlns="{yin}" name="test-notification">
                <description>
                    <text>A test notification</text>
                </description>
                <if-feature name="test-feature"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <anyxml name="notification-anyxml"/>
                <choice name="notification-choice"/>
                <container name="notification-container"/>
                <leaf name="notification-leaf">
                    <type name="inner-type">
                        <typedef name="inner-type">
                            <type name="string"/>
                        </typedef>
                    </type>
                </leaf>
                <leaf-list name="notification-leaf-list">
                    <type name="string"/>
                </leaf-list>
                <list name="notification-list"/>
                <leaf name="grouped-leaf">
                    <type name="string"/>
                </leaf>
            </notification>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class RpcTestCase(xmlunittest.XmlTestCase):

    def test_rpc(self):
        rpc_elem = CONSOLIDATED_MODEL.find(
            'yin:rpc[@name="test-rpc"]', namespaces=NSMAP)
        actual_xml = etree.tostring(rpc_elem)

        expected_xml = """
            <rpc xmlns="{yin}" name="test-rpc">
                <description>
                    <text>A test RPC</text>
                </description>
                <if-feature name="test-feature"/>
                <reference>
                    <text>RFC 6020</text>
                </reference>
                <status value="current"/>
                <input>
                    <anyxml name="input-anyxml"/>
                    <choice name="input-choice"/>
                    <container name="input-container"/>
                    <leaf name="input-leaf">
                        <type name="input-type">
                            <typedef name="input-type">
                                <type name="string"/>
                            </typedef>
                        </type>
                    </leaf>
                    <leaf-list name="input-leaf-list">
                        <type name="inner-type">
                            <typedef name="inner-type">
                                <type name="string"/>
                            </typedef>
                        </type>
                    </leaf-list>
                    <list name="input-list"/>
                    <leaf name="grouped-leaf">
                        <type name="string"/>
                    </leaf>
                    <anyxml name="grouped-anyxml"/>
                </input>
                <output>
                    <anyxml name="output-anyxml"/>
                    <choice name="output-choice"/>
                    <container name="output-container"/>
                    <leaf name="output-leaf">
                        <type name="output-type">
                            <typedef name="output-type">
                                <type name="string"/>
                            </typedef>
                        </type>
                    </leaf>
                    <leaf-list name="output-leaf-list">
                        <type name="inner-type">
                            <typedef name="inner-type">
                                <type name="string"/>
                            </typedef>
                        </type>
                    </leaf-list>
                    <list name="output-list"/>
                    <leaf name="grouped-leaf">
                        <type name="string"/>
                    </leaf>
                    <anyxml name="grouped-anyxml"/>
                </output>
            </rpc>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class TypedefTestCase(xmlunittest.XmlTestCase):

    def test_typedefs_expanded(self):
        leaf_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf[@name="leaf-with-typedef"]', namespaces=NSMAP)
        actual_xml = etree.tostring(leaf_elem)

        expected_xml = """
            <leaf xmlns="{yin}" name="leaf-with-typedef">
                <type name="derived-typedef">
                    <typedef name="derived-typedef">
                        <type name="base-typedef">
                            <length value="11 | 42..max"/>
                            <typedef name="base-typedef">
                                <default value="bumfuzzling"/>
                                <description>
                                    <text>A base typedef</text>
                                </description>
                                <reference>
                                    <text>RFC 6020</text>
                                </reference>
                                <status value="current"/>
                                <type name="string">
                                    <length value="1..255"/>
                                </type>
                                <units name="nonsense"/>
                            </typedef>
                        </type>
                    </typedef>
                </type>
            </leaf>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class LeafrefTestCase(xmlunittest.XmlTestCase):

    def test_leafref_type_resolved(self):
        leaf_elem = CONSOLIDATED_MODEL.find(
            'yin:leaf[@name="leaf-with-leafref"]', namespaces=NSMAP)
        actual_xml = etree.tostring(leaf_elem)

        expected_xml = """
            <leaf xmlns="{yin}" name="leaf-with-leafref">
                <type name="leafref">
                    <path value="../root-leaf"/>
                    <type name="string"/>
                </type>
            </leaf>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)


class AugmentTestCase(xmlunittest.XmlTestCase):

    def setUp(self):
        self.augmented_container_elem = CONSOLIDATED_MODEL.find(
            'yin:container[@name="augmented-container"]', namespaces=NSMAP)

    def test_number_of_children(self):
        self.assertEqual(8, len(self.augmented_container_elem))

    def test_augmenting_leaf_internal(self):
        augmenting_leaf_internal_elem = self.augmented_container_elem.find(
            'yin:leaf[@name="augmenting-leaf-internal"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_leaf_internal_elem)

        expected_xml = """
            <leaf xmlns="{yin}" name="augmenting-leaf-internal">
                <type name="string"/>
            </leaf>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_leaf_internal_elem.nsmap)

    def test_augmenting_anyxml(self):
        augmenting_anyxml_elem = self.augmented_container_elem.find(
            'yin:anyxml[@name="augmenting-anyxml"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_anyxml_elem)

        expected_xml = """
            <anyxml xmlns="{yin}"
                    name="augmenting-anyxml"
                    module-prefix="aug">
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </anyxml>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_anyxml_elem.nsmap)

    def test_augmenting_choice(self):
        augmenting_choice_elem = self.augmented_container_elem.find(
            'yin:choice[@name="augmenting-choice"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_choice_elem)

        expected_xml = """
            <choice xmlns="{yin}"
                    name="augmenting-choice"
                    module-prefix="aug">
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </choice>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_choice_elem.nsmap)

    def test_augmenting_container(self):
        augmenting_container_elem = self.augmented_container_elem.find(
            'yin:container[@name="augmenting-container"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_container_elem)

        expected_xml = """
            <container xmlns="{yin}"
                       xmlns:t="{test}"
                       name="augmenting-container"
                       module-prefix="aug">
                <t:test-extension>extension used in external augment</t:test-extension>
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </container>
            """.format(**NSMAP)  # nopep8

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_container_elem.nsmap)

    def test_augmenting_leaf(self):
        augmenting_leaf_elem = self.augmented_container_elem.find(
            'yin:leaf[@name="augmenting-leaf"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_leaf_elem)

        expected_xml = """
            <leaf xmlns="{yin}"
                  name="augmenting-leaf"
                  module-prefix="aug">
                <type name="string"/>
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </leaf>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_leaf_elem.nsmap)

    def test_augmenting_leaf_list(self):
        augmenting_leaf_list_elem = self.augmented_container_elem.find(
            'yin:leaf-list[@name="augmenting-leaf-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_leaf_list_elem)

        expected_xml = """
            <leaf-list xmlns="{yin}"
                       name="augmenting-leaf-list"
                       module-prefix="aug">
                <type name="string"/>
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </leaf-list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_leaf_list_elem.nsmap)

    def test_augmenting_list(self):
        augmenting_list_elem = self.augmented_container_elem.find(
            'yin:list[@name="augmenting-list"]', namespaces=NSMAP)
        actual_xml = etree.tostring(augmenting_list_elem)

        expected_xml = """
            <list xmlns="{yin}"
                  name="augmenting-list"
                  module-prefix="aug">
                <config value="false"/>
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </list>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, augmenting_list_elem.nsmap)

    def test_uses_in_augment(self):
        grouped_anyxml_elem = self.augmented_container_elem.find(
            'yin:anyxml[@name="grouped-anyxml"]', namespaces=NSMAP)
        actual_xml = etree.tostring(grouped_anyxml_elem)

        expected_xml = """
            <anyxml xmlns="{yin}"
                    name="grouped-anyxml"
                    module-prefix="aug">
                <if-feature name="t:test-feature"/>
                <when condition="/t:root-leaf != 'nonsense'"
                      context-node="parent"/>
            </anyxml>
            """.format(**NSMAP)

        self.assertXmlEquivalentOutputs(actual_xml, expected_xml)

        expected_nsmap = {
            'yin': YIN_NAMESPACE,
            'test': TEST_NAMESPACE,
            't': TEST_NAMESPACE,
            'aug': AUGMENTING_NAMESPACE
        }
        self.assertEqual(expected_nsmap, grouped_anyxml_elem.nsmap)


if __name__ == '__main__':
    unittest.main()
