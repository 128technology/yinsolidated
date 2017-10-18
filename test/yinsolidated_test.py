###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""Unit tests for the yinsolidated module"""

import os

import pytest

import yinsolidated


_NSMAP = {'yin': 'urn:ietf:params:xml:ns:yang:yin:1'}

_TEST_CONSOLIDATED_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    'model.xml'
)


def test_parse_file():
    model_tree = yinsolidated.parse(_TEST_CONSOLIDATED_MODEL_PATH)
    module_element = model_tree.getroot()
    container_element = module_element.find(
        'yin:container[@name="test"]', namespaces=_NSMAP)

    assert container_element.name == 'test'


class TestYinElement(object):

    def test_keyword(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert module_elem.keyword == 'module'

    def test_namespace_map(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:a="alpha"
                    xmlns:b="bravo"/>
            """)

        assert module_elem.namespace_map == {'a': 'alpha', 'b': 'bravo'}

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

        assert module_elem.description == (
            'This is a long description of the data model that wraps onto the '
            'next line'
        )

    def test_no_description(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert module_elem.description is None

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

        assert len(list(module_elem.iterate_data_definitions())) == 7

    def test_rpc_definitions(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <namespace uri="test:ns"/>
                <prefix value="t"/>
                <rpc name="do-something">
                    <input/>
                    <output/>
                </rpc>
                <rpc name="do-something-else">
                    <input/>
                    <output/>
                </rpc>
            </module>
            """)

        assert len(list(module_elem.iterate_rpcs())) == 2


@pytest.fixture
def ancestor_data_node_model():
    return yinsolidated.fromstring("""
        <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
            <namespace uri="test:ns"/>
            <prefix value="t"/>
            <container name="test-container">
                <list name="test-list">
                    <choice name="test-choice">
                        <case name="case-0">
                            <leaf name="test-leaf">
                                <type name="uint8"/>
                            </leaf>
                        </case>
                        <case name="case-1">
                            <leaf-list name="test-leaf-list">
                                <type name="string"/>
                            </leaf-list>
                        </case>
                    </choice>
                </list>
            </container>
        </module>
        """)


class TestGetAncestorDataNodes(object):

    def test_from_leaf_type(self, ancestor_data_node_model):
        type_elem = ancestor_data_node_model.find(
            './/yin:leaf/yin:type',
            namespaces=_NSMAP
        )

        data_node_ancestors = type_elem.get_ancestor_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf'

    def test_from_leaf(self, ancestor_data_node_model):
        leaf_elem = ancestor_data_node_model.find(
            './/yin:leaf',
            namespaces=_NSMAP
        )

        data_node_ancestors = leaf_elem.get_ancestor_data_nodes()
        assert len(data_node_ancestors) == 2
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'

    def test_from_leaf_list_type(self, ancestor_data_node_model):
        type_elem = ancestor_data_node_model.find(
            './/yin:leaf-list/yin:type',
            namespaces=_NSMAP
        )

        data_node_ancestors = type_elem.get_ancestor_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf-list'

    def test_from_leaf_list(self, ancestor_data_node_model):
        leaf_list_elem = ancestor_data_node_model.find(
            './/yin:leaf-list',
            namespaces=_NSMAP
        )

        data_node_ancestors = leaf_list_elem.get_ancestor_data_nodes()
        assert len(data_node_ancestors) == 2
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'


class TestGetAncestorOrSelfDataNodes(object):

    def test_from_leaf_type(self, ancestor_data_node_model):
        type_elem = ancestor_data_node_model.find(
            './/yin:leaf/yin:type',
            namespaces=_NSMAP
        )

        data_node_ancestors = type_elem.get_ancestor_or_self_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf'

    def test_from_leaf(self, ancestor_data_node_model):
        leaf_elem = ancestor_data_node_model.find(
            './/yin:leaf',
            namespaces=_NSMAP
        )

        data_node_ancestors = leaf_elem.get_ancestor_or_self_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf'

    def test_from_leaf_list_type(self, ancestor_data_node_model):
        type_elem = ancestor_data_node_model.find(
            './/yin:leaf-list/yin:type',
            namespaces=_NSMAP
        )

        data_node_ancestors = type_elem.get_ancestor_or_self_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf-list'

    def test_from_leaf_list(self, ancestor_data_node_model):
        leaf_list_elem = ancestor_data_node_model.find(
            './/yin:leaf-list',
            namespaces=_NSMAP
        )

        data_node_ancestors = leaf_list_elem.get_ancestor_or_self_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == 'container'
        assert data_node_ancestors[1].keyword == 'list'
        assert data_node_ancestors[2].keyword == 'leaf-list'


class TestModuleElement(object):

    @pytest.fixture
    def module_elem(self):
        return yinsolidated.fromstring("""
            <module name="test"
                    xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:t="test:ns"
                    module-prefix="t">
            </module>
            """)

    def test_name(self, module_elem):
        assert module_elem.name == 'test'

    def test_namespace(self, module_elem):
        assert module_elem.namespace == 'test:ns'

    def test_prefix(self, module_elem):
        assert module_elem.prefix == 't'


class TestDefinitionElement(object):

    def test_name(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system"
                    xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert choice_elem.name == 'system'

    def test_namespace_from_module(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    xmlns:test="test:ns"
                    module-prefix="test">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        assert choice_elem.namespace == 'test:ns'

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

        assert choice_elem.namespace == 'inner:ns'

    def test_prefix_from_module(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                    module-prefix="test">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        assert choice_elem.prefix == 'test'

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

        assert choice_elem.prefix == 'inner'

    def test_missing_prefix(self):
        module_elem = yinsolidated.fromstring("""
            <module xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <choice/>
            </module>
            """)
        choice_elem = module_elem.find('yin:choice', namespaces=_NSMAP)

        with pytest.raises(yinsolidated.MissingPrefixError):
            choice_elem.prefix

    def test_status(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system" xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <status value='obsolete'/>
            </choice>
            """)

        assert choice_elem.status == 'obsolete'

    def test_default_status(self):
        choice_elem = yinsolidated.fromstring("""
            <choice name="system" xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert choice_elem.status == 'current'


class TestRpcElement(object):

    def test_input(self):
        rpc_elem = yinsolidated.fromstring("""
            <rpc xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <input/>
            </rpc>
            """)

        assert rpc_elem.input is not None

    def test_output(self):
        rpc_elem = yinsolidated.fromstring("""
            <rpc xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <output/>
            </rpc>
            """)

        assert rpc_elem.output is not None


class TestDataDefinitionElement(object):

    def test_is_config_false(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <config value="false"/>
            </choice>
            """)

        assert not choice_elem.is_config

    def test_is_config_no_parent(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert choice_elem.is_config

    def test_is_config_parent_false(self):
        choice_elem = yinsolidated.fromstring("""
            <choice xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <config value="false"/>
                <leaf/>
            </choice>
            """)
        leaf_elem = choice_elem[1]

        assert not leaf_elem.is_config

    def test_when_elements(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <when condition="false"/>
                <when condition="true"/>
            </container>
            """)

        assert len(container_elem.when_elements) == 2


class TestContainerElement(object):

    def test_presence(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <presence value="My existence is meaningful"/>
            </container>
            """)

        assert container_elem.presence == 'My existence is meaningful'

    def test_no_presence(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert container_elem.presence is None


class TestLeafElement(object):

    def test_type(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <type name="uint8"/>
            </leaf>
            """)

        assert leaf_elem.type.base_type.name == 'uint8'

    def test_default(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <default value="600"/>
            </leaf>
            """)

        assert leaf_elem.default == '600'

    def test_no_default(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_elem.default is None

    def test_units(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <units name="seconds"/>
            </leaf>
            """)

        assert leaf_elem.units == 'seconds'

    def test_no_units(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_elem.units is None

    def test_is_mandatory(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="true"/>
            </leaf>
            """)

        assert leaf_elem.is_mandatory

    def test_not_mandatory(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="false"/>
            </leaf>
            """)

        assert not leaf_elem.is_mandatory

    def test_not_mandatory_implicit(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert not leaf_elem.is_mandatory

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

        assert leaf_elem.is_list_key

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

        assert not leaf_elem.is_list_key

    def test_non_list_child_not_key(self):
        leaf_elem = yinsolidated.fromstring("""
            <leaf xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert not leaf_elem.is_list_key


class TestLeafListElement(object):

    def test_type(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <type name="uint8"/>
            </leaf-list>
            """)

        assert leaf_list_elem.type.base_type.name == 'uint8'

    def test_units(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <units name="seconds"/>
            </leaf-list>
            """)

        assert leaf_list_elem.units == 'seconds'

    def test_no_units(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_list_elem.units is None

    def test_min_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <min-elements value="10"/>
            </leaf-list>
            """)

        assert leaf_list_elem.min_elements == 10

    def test_no_min_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_list_elem.min_elements == 0

    def test_max_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <max-elements value="10"/>
            </leaf-list>
            """)

        assert leaf_list_elem.max_elements == 10

    def test_no_max_elements(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_list_elem.max_elements is None

    def test_ordered_by_user(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <ordered-by value="user"/>
            </leaf-list>
            """)

        assert leaf_list_elem.ordered_by == 'user'

    def test_no_ordered_by(self):
        leaf_list_elem = yinsolidated.fromstring("""
            <leaf-list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert leaf_list_elem.ordered_by == 'system'


class TestListElement(object):

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

        assert list_elem.key_ids == [
            ('alpha', 'alpha:ns'),
            ('bravo', 'bravo:ns'),
            ('charlie', 'charlie:ns')
        ]

    def test_no_keys(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert list_elem.key_ids == []

    def test_unique(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <unique tag="alpha bravo charlie"/>
            </list>
            """)

        assert list_elem.unique == ['alpha', 'bravo', 'charlie']

    def test_min_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <min-elements value="10"/>
            </list>
            """)

        assert list_elem.min_elements == 10

    def test_no_min_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert list_elem.min_elements == 0

    def test_max_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <max-elements value="10"/>
            </list>
            """)

        assert list_elem.max_elements == 10

    def test_no_max_elements(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert list_elem.max_elements is None

    def test_ordered_by_user(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <ordered-by value="user"/>
            </list>
            """)

        assert list_elem.ordered_by == 'user'

    def test_no_ordered_by(self):
        list_elem = yinsolidated.fromstring("""
            <list xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert list_elem.ordered_by == 'system'


class TestAnyxmlElement(object):

    def test_is_mandatory(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="true"/>
            </anyxml>
            """)

        assert anyxml_elem.is_mandatory

    def test_not_mandatory(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <mandatory value="false"/>
            </anyxml>
            """)

        assert not anyxml_elem.is_mandatory

    def test_not_mandatory_implicit(self):
        anyxml_elem = yinsolidated.fromstring("""
            <anyxml xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert not anyxml_elem.is_mandatory


class TestTypeElement(object):

    def test_name(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="counter">
                <typedef name="counter">
                    <type name="uint32"/>
                </typedef>
            </type>
            """)

        assert type_elem.name == 'counter'

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

        assert type_elem.base_type.name == 'uint8'

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

        assert type_elem.base_type.name == 'leafref'

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

        assert type_elem.base_type.name == 'union'

    def test_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="counter">
                <typedef name="counter">
                    <type name="uint32"/>
                </typedef>
            </type>
            """)

        assert type_elem.typedef is not None

    def test_no_typedef(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint32"/>
            """)

        assert type_elem.typedef is None

    def test_bits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="bits">
                <bit name="alpha"/>
                <bit name="bravo"/>
            </type>
            """)

        bit_names = [bit.name for bit in type_elem.bits]
        assert bit_names == ['alpha', 'bravo']

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
        assert bit_names == ['alpha', 'bravo']

    def test_enums(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="enumeration">
                <enum name="alpha"/>
                <enum name="bravo"/>
            </type>
            """)

        enum_names = [enum.name for enum in type_elem.enums]
        assert enum_names == ['alpha', 'bravo']

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
        assert enum_names == ['alpha', 'bravo']

    def test_fraction_digits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="decimal64">
                <fraction-digits value="2"/>
            </type>
            """)

        assert type_elem.fraction_digits == '2'

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

        assert type_elem.fraction_digits == '2'

    def test_no_fraction_digits(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
            </type>
            """)

        assert type_elem.fraction_digits is None

    def test_base_identity(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="identityref">
                <base name="base-identity"/>
            </type>
            """)

        assert type_elem.base_identity == 'base-identity'

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

        assert type_elem.base_identity == 'base-identity'

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
                <identity xmlns:t="test:ns"
                          module-prefix="t"
                          name="nested-derived-identity">
                    <base name="derived-identity"/>
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

        assert len(identities) == 2
        assert identities[0].name == 'derived-identity'
        assert identities[1].name == 'nested-derived-identity'

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

        assert len(identities) == 1
        assert identities[0].name == 'another-derived-identity'

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

        with pytest.raises(yinsolidated.MissingIdentityError):
            type_elem.get_identities()

    def test_no_identities(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
            </type>
            """)

        assert len(type_elem.get_identities()) == 0

    def test_length(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="string">
                <length value="1..253"/>
            </type>
            """)

        assert type_elem.length == '1..253'

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

        assert type_elem.length == '1..253'

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

        assert type_elem.length == '8..110'

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

        assert type_elem.length == '9..17'

    def test_no_length(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1" name="string"/>
            """)

        assert type_elem.length is None

    def test_path(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <path value="/a/fake/path"/>
            </type>
            """)

        assert type_elem.path == '/a/fake/path'

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

        assert type_elem.path == '/a/fake/path'

    def test_no_path(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1" name="string"/>
            """)

        assert type_elem.path is None

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

        assert len(type_elem.patterns) == 2

        assert type_elem.patterns[0].value == r'[a-zA-Z0-9_\-]*'
        assert type_elem.patterns[0].error_message == 'Must be alphanumeric'

        assert type_elem.patterns[1].value == '.*'
        assert type_elem.patterns[1].error_message is None

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

        assert len(type_elem.patterns) == 2

        assert type_elem.patterns[0].value == r'[a-zA-Z0-9_\-]*'
        assert type_elem.patterns[0].error_message == 'Must be alphanumeric'

        assert type_elem.patterns[1].value == '.*'
        assert type_elem.patterns[1].error_message is None

    def test_range(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint8">
                <range value="1..253"/>
            </type>
            """)

        assert type_elem.range == '1..253'

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

        assert type_elem.range == '1..253'

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

        assert type_elem.range == '7..9'

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

        assert type_elem.range == '4..128'

    def test_no_range(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="uint8"/>
            """)

        assert type_elem.range is None

    def test_referenced_type_for_leafref(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <type name="string"/>
            </type>
            """)

        assert type_elem.referenced_type.base_type.name == 'string'

    def test_referenced_type_for_union(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="union">
                <type name="uint8"/>
                <type name="string"/>
            </type>
            """)

        assert type_elem.referenced_type is None

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

        assert type_elem.referenced_type.base_type.name == 'string'

    def test_subtypes_for_union(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="union">
                <type name="uint8"/>
                <type name="string"/>
            </type>
            """)

        subtype_names = [elem.base_type.name for elem in type_elem.subtypes]
        assert subtype_names == ['uint8', 'string']

    def test_subtypes_for_leafref(self):
        type_elem = yinsolidated.fromstring("""
            <type xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="leafref">
                <type name="uint8"/>
            </type>
            """)

        assert len(type_elem.subtypes) == 0

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
        assert subtype_names == ['uint8', 'string']


class TestTypedefElement(object):

    def test_name(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
            </typedef>
            """)

        assert typedef_elem.name == 'counter'

    def test_type(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <type name="uint32"/>
            </typedef>
            """)

        assert typedef_elem.type.name == 'uint32'

    def test_default(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <default value="600"/>
            </typedef>
            """)

        assert typedef_elem.default == '600'

    def test_no_default(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter"/>
            """)

        assert typedef_elem.default is None

    def test_units(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter">
                <units name="seconds"/>
            </typedef>
            """)

        assert typedef_elem.units == 'seconds'

    def test_no_units(self):
        typedef_elem = yinsolidated.fromstring("""
            <typedef xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                     name="counter"/>
            """)

        assert typedef_elem.units is None


class TestBitElement(object):

    def test_name(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                 name="alpha"/>
            """)

        assert bit_elem.name == 'alpha'

    def test_position(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <position value="1"/>
            </bit>
            """)

        assert bit_elem.position == 1

    def test_no_position(self):
        bit_elem = yinsolidated.fromstring("""
            <bit xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert bit_elem.position is None


class TestEnumElement(object):

    def test_name(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  name="alpha"/>
            """)

        assert enum_elem.name == 'alpha'

    def test_value(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1">
                <value value="1"/>
            </enum>
            """)

        assert enum_elem.value == 1

    def test_no_value(self):
        enum_elem = yinsolidated.fromstring("""
            <enum xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert enum_elem.value is None


class TestWhenElement(object):

    def test_no_prefix_added(self):
        container_elem = yinsolidated.fromstring("""
            <container xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                       xmlns:t="test:ns"
                       module-prefix="t">
                <when condition="t:foo = 'bar'"/>
            </container>
            """)
        when_element = container_elem.find('yin:when', namespaces=_NSMAP)

        assert when_element.condition == "t:foo = 'bar'"
        assert when_element.namespace_map == {'t': 'test:ns'}

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

        assert when_element.condition == (
            "../d:foo/d:bar = 'alpha' | /t:root/d:test = 'bravo'"
        )

        assert when_element.namespace_map == {
            'd': 'default:ns',
            't': 'test:ns'
        }

    def test_self_context(self):
        when_element = yinsolidated.fromstring("""
            <when xmlns="urn:ietf:params:xml:ns:yang:yin:1"/>
            """)

        assert not when_element.context_node_is_parent

    def test_parent_context(self):
        when_element = yinsolidated.fromstring("""
            <when xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                  context-node="parent"/>
            """)

        assert when_element.context_node_is_parent


class TestIdentityElement(object):

    def test_name(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      name="test-identity"/>
            """)

        assert identity_elem.name == 'test-identity'

    def test_namespace(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity"/>
            """)

        assert identity_elem.namespace == 'test:ns'

    def test_prefix(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity"/>
            """)

        assert identity_elem.prefix == 't'

    def test_no_base(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      name="test-identity"/>
            """)

        assert identity_elem.base == (None, None)

    def test_base_in_same_namespace(self):
        identity_elem = yinsolidated.fromstring("""
            <identity xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                      xmlns:t="test:ns"
                      module-prefix="t"
                      name="test-identity">
                <base name="base-identity"/>
            </identity>
            """)

        assert identity_elem.base == ('base-identity', 'test:ns')

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

        assert identity_elem.base == ('base-identity', 'other:ns')

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
        assert base_identity.name == 'base-identity'

        derived_identities = base_identity.get_derived_identities()

        assert len(derived_identities) == 2
        assert derived_identities[0].name == 'derived-identity-1'
        assert derived_identities[1].name == 'external-derived-identity'
