# Copyright 2016 128 Technology, Inc.

"""Unit tests for the yinsolidated module"""

from __future__ import unicode_literals

import types

import pytest

import yinsolidated


class TestYinElement(object):
    def test_keyword(self):
        module_elem = yinsolidated.parse_json({"keyword": "module"})

        assert module_elem.keyword == "module"

    def test_namespace_from_module(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "t",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1", "t": "test:ns"},
                "children": [{"keyword": "choice"}],
            }
        )
        choice_elem = module_elem.find("choice")

        assert choice_elem.namespace == "test:ns"

    def test_namespace_from_augmenting_node(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "out",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "nsmap": {
                    "yin": "urn:ietf:params:xml:ns:yang:yin:1",
                    "out": "outer:ns",
                },
                "children": [
                    {
                        "keyword": "test-container",
                        "module-prefix": "in",
                        "nsmap": {"in": "inner:ns"},
                        "children": [{"keyword": "choice"}],
                    }
                ],
            }
        )
        choice_elem = module_elem.find("test-container").find("choice")

        assert choice_elem.namespace == "inner:ns"

    def test_module_name_from_module(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-name": "test-module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [{"keyword": "choice"}],
            }
        )
        choice_elem = module_elem.find("choice")

        assert choice_elem.module_name == "test-module"

    def test_module_name_from_augmenting_node(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-name": "test-module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [
                    {
                        "keyword": "container",
                        "module-name": "inner-module",
                        "children": [{"keyword": "choice"}],
                    }
                ],
            }
        )
        choice_elem = module_elem.find("container").find("choice")

        assert choice_elem.module_name == "inner-module"

    def test_missing_module_name(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [{"keyword": "container", "name": "test"}],
            }
        )
        choice_elem = module_elem.find("container")

        with pytest.raises(
            yinsolidated.MissingModuleNameError,
            match="No module-name attribute found for ancestors of container 'test'",
        ):
            _ = choice_elem.module_name

    def test_prefix_from_module(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "test",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [{"keyword": "choice"}],
            }
        )
        choice_elem = module_elem.find("choice")

        assert choice_elem.prefix == "test"

    def test_prefix_from_augmenting_node(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "outer",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [
                    {
                        "keyword": "container",
                        "module-prefix": "inner",
                        "children": [{"keyword": "choice"}],
                    }
                ],
            }
        )
        choice_elem = module_elem.find("container").find("choice")

        assert choice_elem.prefix == "inner"

    def test_missing_prefix(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [{"keyword": "container", "name": "test"}],
            }
        )
        choice_elem = module_elem.find("container")

        with pytest.raises(
            yinsolidated.MissingPrefixError,
            match="No prefix attribute found for ancestors of container 'test'",
        ):
            _ = choice_elem.prefix

    def test_description(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [{"keyword": "description", "text": "short description"}],
            }
        )

        assert module_elem.description == "short description"

    def test_description(self):
        module_elem = yinsolidated.parse_json({"keyword": "module",})

        assert module_elem.description is None

    def test_child_data_definitions(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1"},
                "children": [
                    {"keyword": "container"},
                    {"keyword": "list"},
                    {"keyword": "choice"},
                    {"keyword": "case"},
                    {"keyword": "foobar"},
                    {"keyword": "leaf-list"},
                    {"keyword": "leaf"},
                    {"keyword": "anyxml"},
                    {"keyword": "rpc"},
                ],
            }
        )

        assert len(list(module_elem.iterate_data_definitions())) == 7


@pytest.fixture
def ancestor_data_node_model():
    return yinsolidated.parse_json(
        {
            "keyword": "module",
            "children": [
                {
                    "keyword": "container",
                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    "name": "test-container",
                    "children": [
                        {
                            "keyword": "list",
                            "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            "name": "test-list",
                            "children": [
                                {
                                    "keyword": "choice",
                                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    "name": "test-choice",
                                    "children": [
                                        {
                                            "keyword": "case",
                                            "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                            "name": "case-0",
                                            "children": [
                                                {
                                                    "keyword": "leaf",
                                                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                    "children": [
                                                        {
                                                            "keyword": "type",
                                                            "name": "uint8",
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "keyword": "case",
                                            "name": "case-1",
                                            "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                            "children": [
                                                {
                                                    "keyword": "leaf-list",
                                                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                    "children": [
                                                        {
                                                            "keyword": "type",
                                                            "name": "string",
                                                        },
                                                    ],
                                                },
                                                {
                                                    "keyword": "container",
                                                    "name": "nested-container",
                                                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                },
                                            ],
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                },
                {
                    "keyword": "list",
                    "name": "sibling-list",
                    "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                },
                {
                    "keyword": "container",
                    "name": "sibling-container",
                    "namespace": "not:yin:ns",
                },
            ],
        }
    )


class TestGetAncestorDataNodes(object):
    def test_from_leaf_type(self, ancestor_data_node_model):
        type_elem = (
            ancestor_data_node_model.find("container")
            .find("list")
            .find("choice")
            .find("case")
            .find("leaf")
            .find("type")
        )

        data_node_ancestors = type_elem.get_ancestor_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == "container"
        assert data_node_ancestors[1].keyword == "list"
        assert data_node_ancestors[2].keyword == "leaf"


class TestGetAncestorOrSelfDataNodes(object):
    def test_from_leaf_type(self, ancestor_data_node_model):
        type_elem = (
            ancestor_data_node_model.find("container")
            .find("list")
            .find("choice")
            .find("case")
            .find("leaf")
            .find("type")
        )

        data_node_ancestors = type_elem.get_ancestor_or_self_data_nodes()
        assert len(data_node_ancestors) == 3
        assert data_node_ancestors[0].keyword == "container"
        assert data_node_ancestors[1].keyword == "list"
        assert data_node_ancestors[2].keyword == "leaf"


class TestFind(object):
    def test_find(self, ancestor_data_node_model):
        assert ancestor_data_node_model.find("container").name == "test-container"

    def test_find_failure(self, ancestor_data_node_model):
        assert ancestor_data_node_model.find("leaf") is None

    def test_find_with_namespace(self, ancestor_data_node_model):
        assert (
            ancestor_data_node_model.find(
                "container", namespace="urn:ietf:params:xml:ns:yang:yin:1"
            ).name
            == "test-container"
        )

    def test_find_with_namespace_failure(self, ancestor_data_node_model):
        assert ancestor_data_node_model.find("container", namespace="bad:ns") is None

    @pytest.mark.parametrize(
        "keyword, namespace, recursive, expected_count",
        [
            pytest.param("container", None, False, 2, id="without_namespace"),
            pytest.param(
                "container",
                "urn:ietf:params:xml:ns:yang:yin:1",
                False,
                1,
                id="with_namespace",
            ),
            pytest.param("container", None, True, 3, id="recursive_without_namespac"),
            pytest.param(
                "container",
                "urn:ietf:params:xml:ns:yang:yin:1",
                True,
                2,
                id="recursive_with_namespace",
            ),
            pytest.param("leaf", None, False, 0, id="missing"),
            pytest.param("bad", None, True, 0, id="recursive_missing"),
        ],
    )
    def test_findall(
        self, ancestor_data_node_model, keyword, namespace, recursive, expected_count
    ):
        iter_results = ancestor_data_node_model.iterfind(
            keyword, namespace=namespace, recursive=recursive
        )

        assert isinstance(iter_results, types.GeneratorType)
        assert len(list(iter_results)) == expected_count

        results = ancestor_data_node_model.findall(
            keyword, namespace=namespace, recursive=recursive
        )

        assert len(results) == expected_count


class TestModuleElement(object):
    def test_name(self):
        module_elem = yinsolidated.parse_json({"keyword": "module", "name": "test"})

        assert module_elem.name == "test"


class TestDefinitionElement(object):
    def test_name(self):
        choice_elem = yinsolidated.parse_json({"keyword": "choice", "name": "system"})

        assert choice_elem.name == "system"

    def test_status(self):
        choice_elem = yinsolidated.parse_json(
            {
                "keyword": "choice",
                "children": [
                    {
                        "keyword": "status",
                        "value": "obsolete",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert choice_elem.status == "obsolete"

    def test_default_status(self):
        choice_elem = yinsolidated.parse_json({"keyword": "choice"})

        assert choice_elem.status == "current"


class TestDataDefinitionElement(object):
    def test_is_config_false(self):
        choice_elem = yinsolidated.parse_json(
            {
                "keyword": "choice",
                "children": [
                    {
                        "keyword": "config",
                        "value": "false",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert not choice_elem.is_config

    def test_is_config_no_parent(self):
        choice_elem = yinsolidated.parse_json({"keyword": "choice",})

        assert choice_elem.is_config

    def test_is_config_parent_false(self):
        choice_elem = yinsolidated.parse_json(
            {
                "keyword": "choice",
                "module-prefix": "t",
                "nsmap": {"yin": "urn:ietf:params:xml:ns:yang:yin:1", "t": "test:ns"},
                "children": [
                    {
                        "keyword": "config",
                        "value": "false",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {"keyword": "leaf"},
                ],
            }
        )
        leaf_elem = choice_elem.find("leaf")

        assert not leaf_elem.is_config

    def test_when_elements(self):
        container_elem = yinsolidated.parse_json(
            {
                "keyword": "container",
                "children": [
                    {
                        "keyword": "when",
                        "condition": "xxx",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "when",
                        "condition": "yyy",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            }
        )

        assert len(container_elem.when_elements) == 2


class TestContainerElement(object):
    def test_presence(self):
        container_elem = yinsolidated.parse_json(
            {
                "keyword": "container",
                "children": [
                    {
                        "keyword": "presence",
                        "value": "My existence is meaningful",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            }
        )

        assert container_elem.presence == "My existence is meaningful"

    def test_no_presence(self):
        container_elem = yinsolidated.parse_json({"keyword": "container"})

        assert container_elem.presence is None


class TestLeafElement(object):
    def test_type(self):
        leaf_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint8",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_elem.type.base_type.name == "uint8"

    def test_default(self):
        leaf_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "children": [
                    {
                        "keyword": "default",
                        "value": "600",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_elem.default == "600"

    def test_no_default(self):
        leaf_elem = yinsolidated.parse_json({"keyword": "leaf"})

        assert leaf_elem.default is None

    def test_units(self):
        leaf_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "children": [
                    {
                        "keyword": "units",
                        "name": "seconds",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_elem.units == "seconds"

    def test_no_units(self):
        leaf_elem = yinsolidated.parse_json({"keyword": "leaf"})

        assert leaf_elem.units is None

    def test_is_mandatory(self):
        leaf_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "children": [
                    {
                        "keyword": "mandatory",
                        "value": "true",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_elem.is_mandatory

    def test_not_mandatory(self):
        leaf_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "children": [
                    {
                        "keyword": "mandatory",
                        "value": "false",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert not leaf_elem.is_mandatory

    def test_not_mandatory_implicit(self):
        leaf_elem = yinsolidated.parse_json({"keyword": "leaf"})

        assert not leaf_elem.is_mandatory

    def test_is_list_key(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "key",
                        "value": "alpha",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "leaf",
                        "name": "alpha",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            }
        )
        leaf_elem = list_elem.find("leaf")

        assert leaf_elem.is_list_key

    def test_list_child_not_key(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "key",
                        "value": "bravo",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "leaf",
                        "name": "alpha",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            }
        )
        leaf_elem = list_elem.find("leaf")

        assert not leaf_elem.is_list_key

    def test_non_list_child_not_key(self):
        leaf_elem = yinsolidated.parse_json({"keyword": "leaf"})

        assert not leaf_elem.is_list_key


class TestLeafListElement(object):
    def test_type(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint8",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_list_elem.type.base_type.name == "uint8"

    def test_units(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "units",
                        "name": "seconds",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_list_elem.units == "seconds"

    def test_no_units(self):
        leaf_list_elem = yinsolidated.parse_json({"keyword": "leaf-list"})

        assert leaf_list_elem.units is None

    def test_min_elements(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "min-elements",
                        "value": "10",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_list_elem.min_elements == 10

    def test_no_min_elements(self):
        leaf_list_elem = yinsolidated.parse_json({"keyword": "leaf-list"})

        assert leaf_list_elem.min_elements == 0

    def test_max_elements(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "max-elements",
                        "value": "10",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_list_elem.max_elements == 10

    def test_no_max_elements(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
            }
        )

        assert leaf_list_elem.max_elements is None

    def test_ordered_by_user(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "ordered-by",
                        "value": "user",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert leaf_list_elem.ordered_by == "user"

    def test_no_ordered_by(self):
        leaf_list_elem = yinsolidated.parse_json(
            {
                "keyword": "leaf-list",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
            }
        )

        assert leaf_list_elem.ordered_by == "system"


class TestListElement(object):
    def test_keys(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "c",
                "children": [
                    {
                        "keyword": "list",
                        "nsmap": {"a": "alpha:ns", "b": "bravo:ns", "c": "charlie:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "key",
                                "value": "a:alpha b:bravo charlie",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            },
                        ],
                    },
                ],
            }
        )
        list_elem = module_elem.find("list")

        assert list_elem.key_ids == [
            ("alpha", "alpha:ns"),
            ("bravo", "bravo:ns"),
            ("charlie", "charlie:ns"),
        ]

    def test_no_keys(self):
        list_elem = yinsolidated.parse_json({"keyword": "list"})

        assert list_elem.key_ids == []

    def test_unique(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "children": [
                    {
                        "keyword": "unique",
                        "tag": "alpha bravo charlie",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert list_elem.unique == ["alpha", "bravo", "charlie"]

    def test_min_elements(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "children": [
                    {
                        "keyword": "min-elements",
                        "value": "10",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert list_elem.min_elements == 10

    def test_no_min_elements(self):
        list_elem = yinsolidated.parse_json({"keyword": "list"})

        assert list_elem.min_elements == 0

    def test_max_elements(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "children": [
                    {
                        "keyword": "max-elements",
                        "value": "10",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert list_elem.max_elements == 10

    def test_no_max_elements(self):
        list_elem = yinsolidated.parse_json({"keyword": "list"})

        assert list_elem.max_elements is None

    def test_ordered_by_user(self):
        list_elem = yinsolidated.parse_json(
            {
                "keyword": "list",
                "children": [
                    {
                        "keyword": "ordered-by",
                        "value": "user",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert list_elem.ordered_by == "user"

    def test_no_ordered_by(self):
        list_elem = yinsolidated.parse_json({"keyword": "list"})

        assert list_elem.ordered_by == "system"


class TestAnyxmlElement(object):
    def test_is_mandatory(self):
        anyxml_elem = yinsolidated.parse_json(
            {
                "keyword": "anyxml",
                "children": [
                    {
                        "keyword": "mandatory",
                        "value": "true",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert anyxml_elem.is_mandatory

    def test_not_mandatory(self):
        anyxml_elem = yinsolidated.parse_json(
            {
                "keyword": "anyxml",
                "children": [
                    {
                        "keyword": "mandatory",
                        "value": "false",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert not anyxml_elem.is_mandatory

    def test_not_mandatory_implicit(self):
        anyxml_elem = yinsolidated.parse_json({"keyword": "anyxml"})

        assert not anyxml_elem.is_mandatory


class TestTypeElement(object):
    @pytest.fixture
    def type_elem_with_unprefixed_name(self):
        return yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "module-prefix": "a",
                "nsmap": {"a": "a:ns"},
                "children": [
                    {
                        "keyword": "type",
                        "name": "counter",
                        "nsmap": {"a": "a:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "typedef",
                                "name": "uint32",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    }
                ],
            }
        ).find("type")

    def test_name(self, type_elem_with_unprefixed_name):
        assert type_elem_with_unprefixed_name.name == "counter"

    def test_unprefixed_name(self, type_elem_with_unprefixed_name):
        assert type_elem_with_unprefixed_name.unprefixed_name == "counter"

    def test_prefix(self, type_elem_with_unprefixed_name):
        assert type_elem_with_unprefixed_name.prefix == "a"

    def test_namespace(self, type_elem_with_unprefixed_name):
        assert type_elem_with_unprefixed_name.namespace == "a:ns"

    def test_base(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "counter",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "percentage",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "meter",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "typedef",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                        "name": "meter",
                                        "children": [
                                            {
                                                "keyword": "type",
                                                "name": "uint8",
                                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        )

        assert type_elem.base_type.name == "uint8"

    def test_base_for_leafref(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "test-leafref",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "test-leafref",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "leafref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "type",
                                        "name": "uint32",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        )

        assert type_elem.base_type.name == "leafref"

    def test_base_for_union(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "test-union",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "test-union",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "union",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "type",
                                        "name": "uint32",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                    {
                                        "keyword": "type",
                                        "name": "string",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        )

        assert type_elem.base_type.name == "union"

    def test_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "counter",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "counter",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "uint32",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    }
                ],
            }
        )

        assert type_elem.typedef is not None

    def test_no_typedef(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "uint32"},)

        assert type_elem.typedef is None

    def test_bits(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "bits",
                "children": [
                    {
                        "keyword": "bit",
                        "name": "alpha",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "bit",
                        "name": "bravo",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        bit_names = [bit.name for bit in type_elem.bits]
        assert bit_names == ["alpha", "bravo"]

    def test_bits_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "bits",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "bit",
                                        "name": "alpha",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                    {
                                        "keyword": "bit",
                                        "name": "bravo",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        )

        bit_names = [bit.name for bit in type_elem.bits]
        assert bit_names == ["alpha", "bravo"]

    def test_enums(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "enumeration",
                "children": [
                    {
                        "keyword": "enum",
                        "name": "alpha",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "enum",
                        "name": "bravo",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        enum_names = [enum.name for enum in type_elem.enums]
        assert enum_names == ["alpha", "bravo"]

    def test_enums_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-typedef",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "enumeration",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "enum",
                                        "name": "alpha",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                    {
                                        "keyword": "enum",
                                        "name": "bravo",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
        )

        enum_names = [enum.name for enum in type_elem.enums]
        assert enum_names == ["alpha", "bravo"]

    def test_fraction_digits(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "decimal64",
                "children": [
                    {
                        "keyword": "fraction-digits",
                        "value": "2",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.fraction_digits == "2"

    def test_fraction_digits_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "decimal64",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "fraction-digits",
                                        "value": "2",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
        )

        assert type_elem.fraction_digits == "2"

    def test_no_fraction_digits(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "string"})

        assert type_elem.fraction_digits is None

    def test_base_identity(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "identityref",
                "children": [
                    {
                        "keyword": "base",
                        "name": "base-identity",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.base_identity == "base-identity"

    def test_base_identity_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "identityref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "base",
                                        "name": "base-identity",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        )

        assert type_elem.base_identity == "base-identity"

    def test_identities_base_in_same_namespace(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "identity",
                        "name": "base-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "identity",
                        "name": "derived-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "nested-derived-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "derived-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "another-base-identity",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "module-prefix": "o",
                    },
                    {
                        "keyword": "identity",
                        "name": "another-derived-identity",
                        "module-prefix": "o",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "another-derived-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "leaf",
                        "name": "test-leaf",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "identityref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "base",
                                        "name": "base-identity",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )
        type_elem = module_elem.find("leaf").find("type")

        identities = type_elem.get_identities()

        assert len(identities) == 2
        assert identities[0].name == "derived-identity"
        assert identities[1].name == "nested-derived-identity"

    def test_identities_base_in_different_namespace(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "t",
                "children": [
                    {
                        "keyword": "identity",
                        "name": "base-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "identity",
                        "name": "derived-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "nested-derived-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "derived-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "another-base-identity",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "module-prefix": "o",
                    },
                    {
                        "keyword": "identity",
                        "name": "another-derived-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "o:another-base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "leaf",
                        "name": "test-leaf",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "identityref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "base",
                                        "name": "o:another-base-identity",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )

        type_elem = module_elem.find("leaf").find("type")

        identities = type_elem.get_identities()

        assert len(identities) == 1
        assert identities[0].name == "another-derived-identity"

    def test_missing_identity(self):
        module_elem = yinsolidated.parse_json(
            {
                "keyword": "module",
                "module-prefix": "t",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "leaf",
                        "name": "test-leaf",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "nsmap": {"t": "test:ns"},
                        "children": [
                            {
                                "keyword": "type",
                                "name": "identityref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "base",
                                        "name": "t:base-identity",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        )
        type_elem = module_elem.find("leaf").find("type")

        with pytest.raises(yinsolidated.MissingIdentityError):
            type_elem.get_identities()

    def test_no_identities(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "string"})

        assert len(type_elem.get_identities()) == 0

    def test_length(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "string",
                "children": [
                    {
                        "keyword": "length",
                        "value": "1..253",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.length == "1..253"

    def test_length_typedefs(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "string",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "length",
                                        "value": "1..253",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
        )

        assert type_elem.length == "1..253"

        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "indirect-fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "another-fake-type",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "typedef",
                                        "name": "fake-type",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                        "children": [
                                            {
                                                "keyword": "type",
                                                "name": "string",
                                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                "children": [
                                                    {
                                                        "keyword": "length",
                                                        "value": "8..110",
                                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                    }
                                                ],
                                            },
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
        )

        assert type_elem.length == "8..110"

        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "string",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "length",
                                        "value": "1..17",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "keyword": "length",
                        "value": "9..17",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        assert type_elem.length == "9..17"

    def test_no_length(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "string"},)

        assert type_elem.length is None

    def test_path(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "leafref",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "path",
                        "value": "/a/fake/path",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.path == "/a/fake/path"

    def test_path_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "leafref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "path",
                                        "value": "/a/fake/path",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        )

        assert type_elem.path == "/a/fake/path"

    def test_no_path(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "string"})

        assert type_elem.path is None

    def test_patterns(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "string",
                "children": [
                    {
                        "keyword": "pattern",
                        "value": "[a-zA-Z0-9_\\-]*",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "error-message",
                                "value": "Must be alphanumeric",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "pattern",
                        "value": ".*",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        assert len(type_elem.patterns) == 2

        assert type_elem.patterns[0].value == r"[a-zA-Z0-9_\-]*"
        assert type_elem.patterns[0].error_message == "Must be alphanumeric"

        assert type_elem.patterns[1].value == ".*"
        assert type_elem.patterns[1].error_message is None

    def test_patterns_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "string",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "pattern",
                                        "value": "[a-zA-Z0-9_\\-]*",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                        "children": [
                                            {
                                                "keyword": "error-message",
                                                "value": "Must be alphanumeric",
                                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                            }
                                        ],
                                    },
                                    {
                                        "keyword": "pattern",
                                        "value": ".*",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            },
        )

        assert len(type_elem.patterns) == 2

        assert type_elem.patterns[0].value == r"[a-zA-Z0-9_\-]*"
        assert type_elem.patterns[0].error_message == "Must be alphanumeric"

        assert type_elem.patterns[1].value == ".*"
        assert type_elem.patterns[1].error_message is None

    def test_range(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "uint8",
                "children": [
                    {
                        "keyword": "range",
                        "value": "1..253",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.range == "1..253"

    def test_range_typedefs(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "uint8",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "range",
                                        "value": "1..253",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        )

        assert type_elem.range == "1..253"

        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "wrapper",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "fake-type",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "typedef",
                                        "name": "fake-type",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                        "children": [
                                            {
                                                "keyword": "type",
                                                "name": "uint8",
                                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                "children": [
                                                    {
                                                        "keyword": "range",
                                                        "value": "7..9",
                                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                                    }
                                                ],
                                            },
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        )

        assert type_elem.range == "7..9"

        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "fake-type",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "uint8",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "range",
                                        "value": "1..227",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "keyword": "range",
                        "value": "4..128",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            }
        )

        assert type_elem.range == "4..128"

    def test_no_range(self):
        type_elem = yinsolidated.parse_json({"keyword": "type", "name": "uint8"})

        assert type_elem.range is None

    def test_referenced_type_for_leafref(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "leafref",
                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                "children": [
                    {
                        "keyword": "type",
                        "name": "string",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert type_elem.referenced_type.base_type.name == "string"

    def test_referenced_type_for_union(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "union",
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint8",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "type",
                        "name": "string",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        assert type_elem.referenced_type is None

    def test_referenced_type_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "faketype",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "leafref",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "type",
                                        "name": "string",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
        )

        assert type_elem.referenced_type.base_type.name == "string"

    def test_subtypes_for_union(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "union",
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint8",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "type",
                        "name": "string",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                ],
            },
        )

        subtype_names = [elem.base_type.name for elem in type_elem.subtypes]
        assert subtype_names == ["uint8", "string"]

    def test_subtypes_for_leafref(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "leafref",
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint8",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert len(type_elem.subtypes) == 0

    def test_subtypes_typedef(self):
        type_elem = yinsolidated.parse_json(
            {
                "keyword": "type",
                "name": "fake-type",
                "children": [
                    {
                        "keyword": "typedef",
                        "name": "faketype",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "type",
                                "name": "union",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "type",
                                        "name": "uint8",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                    {
                                        "keyword": "type",
                                        "name": "string",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            },
        )

        subtype_names = [elem.base_type.name for elem in type_elem.subtypes]
        assert subtype_names == ["uint8", "string"]


class TestTypeElementWithPrefixedName(object):
    @pytest.fixture
    def type_elem_with_prefixed_name(self):
        return yinsolidated.parse_json(
            {
                "keyword": "leaf",
                "name": "test-leaf",
                "module-prefix": "a",
                "nsmap": {"a": "a:ns", "b": "b:ns"},
                "children": [
                    {
                        "keyword": "type",
                        "name": "b:counter",
                        "nsmap": {"a": "a:ns", "b": "b:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "typedef",
                                "name": "counter",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                "children": [
                                    {
                                        "keyword": "type",
                                        "name": "uint32",
                                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ).find("type")

    def test_name(self, type_elem_with_prefixed_name):
        assert type_elem_with_prefixed_name.name == "b:counter"

    def test_unprefixed_name(self, type_elem_with_prefixed_name):
        assert type_elem_with_prefixed_name.unprefixed_name == "counter"

    def test_prefix(self, type_elem_with_prefixed_name):
        assert type_elem_with_prefixed_name.prefix == "b"

    def test_namespace(self, type_elem_with_prefixed_name):
        assert type_elem_with_prefixed_name.namespace == "b:ns"


class TestTypedefElement(object):
    def test_name(self):
        typedef_elem = yinsolidated.parse_json(
            {"keyword": "typedef", "name": "counter"},
        )

        assert typedef_elem.name == "counter"

    def test_type(self):
        typedef_elem = yinsolidated.parse_json(
            {
                "keyword": "typedef",
                "name": "counter",
                "children": [
                    {
                        "keyword": "type",
                        "name": "uint32",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert typedef_elem.type.name == "uint32"

    def test_default(self):
        typedef_elem = yinsolidated.parse_json(
            {
                "keyword": "typedef",
                "name": "counter",
                "children": [
                    {
                        "keyword": "default",
                        "value": "600",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert typedef_elem.default == "600"

    def test_no_default(self):
        typedef_elem = yinsolidated.parse_json(
            {"keyword": "typedef", "name": "counter"},
        )

        assert typedef_elem.default is None

    def test_units(self):
        typedef_elem = yinsolidated.parse_json(
            {
                "keyword": "typedef",
                "name": "counter",
                "children": [
                    {
                        "keyword": "units",
                        "name": "seconds",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert typedef_elem.units == "seconds"

    def test_no_units(self):
        typedef_elem = yinsolidated.parse_json(
            {"keyword": "typedef", "name": "counter"},
        )

        assert typedef_elem.units is None


class TestBitElement(object):
    def test_name(self):
        bit_elem = yinsolidated.parse_json({"keyword": "bit", "name": "alpha"})

        assert bit_elem.name == "alpha"

    def test_position(self):
        bit_elem = yinsolidated.parse_json(
            {
                "keyword": "bit",
                "name": "alpha",
                "children": [
                    {
                        "keyword": "position",
                        "value": "1",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert bit_elem.position == 1

    def test_no_position(self):
        bit_elem = yinsolidated.parse_json({"keyword": "bit", "name": "alpha"})

        assert bit_elem.position is None


class TestEnumElement(object):
    def test_name(self):
        enum_elem = yinsolidated.parse_json({"keyword": "enum", "name": "alpha"})

        assert enum_elem.name == "alpha"

    def test_value(self):
        enum_elem = yinsolidated.parse_json(
            {
                "keyword": "enum",
                "name": "alpha",
                "children": [
                    {
                        "keyword": "value",
                        "value": "1",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            },
        )

        assert enum_elem.value == 1

    def test_no_value(self):
        enum_elem = yinsolidated.parse_json({"keyword": "enum", "name": "alpha"})

        assert enum_elem.value is None


class TestWhenElement(object):
    def test_no_prefix_added(self):
        container_elem = yinsolidated.parse_json(
            {
                "keyword": "container",
                "module-prefix": "t",
                "children": [
                    {
                        "keyword": "when",
                        "condition": "t:foo = 'bar'",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "nsmap": {"t": "test:ns"},
                    }
                ],
            },
        )
        when_element = container_elem.find("when")

        assert when_element.condition == "t:foo = 'bar'"
        assert when_element.nsmap == {"t": "test:ns"}

    def test_prefix_added(self):
        container_elem = yinsolidated.parse_json(
            {
                "keyword": "container",
                "module-prefix": "d",
                "children": [
                    {
                        "keyword": "when",
                        "condition": "../foo/bar = 'alpha' | /t:root/test = 'bravo'",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "nsmap": {"t": "test:ns", "d": "default:ns"},
                    }
                ],
            },
        )

        when_element = container_elem.find("when")

        assert when_element.condition == (
            "../d:foo/d:bar = 'alpha' | /t:root/d:test = 'bravo'"
        )

        assert when_element.nsmap == {"d": "default:ns", "t": "test:ns"}

    def test_self_context(self):
        when_element = yinsolidated.parse_json({"keyword": "when"})

        assert not when_element.context_node_is_parent

    def test_parent_context(self):
        when_element = yinsolidated.parse_json(
            {"keyword": "when", "context-node": "parent"},
        )

        assert when_element.context_node_is_parent


class TestIdentityElement(object):
    def test_name(self):
        identity_elem = yinsolidated.parse_json(
            {"keyword": "identity", "name": "test-identity"},
        )

        assert identity_elem.name == "test-identity"

    def test_namespace(self):
        identity_elem = yinsolidated.parse_json(
            {
                "keyword": "identity",
                "module-prefix": "t",
                "name": "test-identity",
                "nsmap": {"t": "test:ns"},
            }
        )

        assert identity_elem.namespace == "test:ns"

    def test_prefix(self):
        identity_elem = yinsolidated.parse_json(
            {
                "keyword": "identity",
                "module-prefix": "t",
                "name": "test-identity",
                "nsmap": {"t": "test:ns"},
            }
        )

        assert identity_elem.prefix == "t"

    def test_no_base(self):
        identity_elem = yinsolidated.parse_json(
            {"keyword": "identity", "name": "test-identity"},
        )

        assert identity_elem.base == (None, None)

    def test_base_in_same_namespace(self):
        identity_elem = yinsolidated.parse_json(
            {
                "keyword": "identity",
                "name": "test-identity",
                "module-prefix": "t",
                "nsmap": {"t": "test:ns"},
                "children": [
                    {
                        "keyword": "base",
                        "name": "base-identity",
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    }
                ],
            }
        )

        assert identity_elem.base == ("base-identity", "test:ns")

        def test_base_in_different_namespace(self):
            identity_elem = yinsolidated.parse_json(
                {
                    "keyword": "identity",
                    "name": "test-identity",
                    "module-prefix": "t",
                    "nsmap": {"t": "test:ns", "o": "other:ns"},
                    "children": [
                        {
                            "keyword": "base",
                            "name": "o:base-identity",
                            "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        }
                    ],
                },
            )

            assert identity_elem.base == ("base-identity", "other:ns")

    def test_iterate_derived_identities(self):
        module_element = yinsolidated.parse_json(
            {
                "keyword": "module",
                "children": [
                    {
                        "keyword": "identity",
                        "name": "base-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "identity",
                        "name": "derived-identity-1",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "another-base-identity",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                    },
                    {
                        "keyword": "identity",
                        "name": "derived-identity-2",
                        "module-prefix": "t",
                        "nsmap": {"t": "test:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "another-base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "external-derived-identity",
                        "module-prefix": "o",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "t:base-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                    {
                        "keyword": "identity",
                        "name": "nested-derived-identity",
                        "module-prefix": "o",
                        "nsmap": {"t": "test:ns", "o": "other:ns"},
                        "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                        "children": [
                            {
                                "keyword": "base",
                                "name": "o:external-derived-identity",
                                "namespace": "urn:ietf:params:xml:ns:yang:yin:1",
                            }
                        ],
                    },
                ],
            },
        )
        base_identity = module_element.find("identity")
        assert base_identity.name == "base-identity"

        derived_identities = base_identity.get_derived_identities()
        print([x.name for x in derived_identities])

        assert len(derived_identities) == 3
        assert derived_identities[0].name == "derived-identity-1"
        assert derived_identities[1].name == "external-derived-identity"
        assert derived_identities[2].name == "nested-derived-identity"

        direct_identities = base_identity.get_directly_derived_identities()

        assert len(direct_identities) == 2
        assert direct_identities[0].name == "derived-identity-1"
        assert direct_identities[1].name == "external-derived-identity"
