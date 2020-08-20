# Copyright 2016 128 Technology, Inc.

"""Unit tests for the yinsolidated pyang plugin"""

from __future__ import unicode_literals

import json
import os
import subprocess

import pyang
import pytest

from yinsolidated.plugin import plugin


YINSOLIDATED_PLUGIN_DIRECTORY = os.path.dirname(plugin.__file__)

YIN_NAMESPACE = "urn:ietf:params:xml:ns:yang:yin:1"
TEST_NAMESPACE = "urn:xml:ns:test"
AUGMENTING_NAMESPACE = "urn:xml:ns:test:augment"
NSMAP = {"yin": YIN_NAMESPACE, "test": TEST_NAMESPACE, "aug": AUGMENTING_NAMESPACE}


@pytest.fixture(scope="module")
def consolidated_model():
    test_file_dir = os.path.dirname(os.path.realpath(__file__))
    modules_dir = os.path.join(test_file_dir, "modules")
    main_module = os.path.join(modules_dir, "test-module.yang")
    augmenting_module = os.path.join(modules_dir, "augmenting-module.yang")

    pyang_command = [
        "pyang",
        "-f",
        "yinsolidated",
        "--yinsolidated-output-format=json",
        "-p",
        modules_dir,
    ]

    if pyang.__version__ < "1.7.2":
        pyang_command.extend(["--plugindir", YINSOLIDATED_PLUGIN_DIRECTORY])

    pyang_command.extend([main_module, augmenting_module])

    consolidated_model_json = subprocess.check_output(pyang_command)

    return json.loads(consolidated_model_json)


def get_nested(yin_element, *path):
    path = list(path)
    last = path.pop()
    for key in path:
        for child in yin_element["children"]:
            if child["keyword"] == key:
                yin_element = child
                break
        else:
            raise KeyError(key)

    return yin_element[last]


class TestModule(object):
    def test_module_root_element(self, consolidated_model):
        assert consolidated_model["keyword"] == "module"

    def test_module_name_attribute(self, consolidated_model):
        module_name = consolidated_model.get("module-name")
        assert module_name == "test-module"

    def test_prefix_attribute(self, consolidated_model):
        prefix = consolidated_model.get("module-prefix")
        assert prefix == "test"

    def test_nsmap(self, consolidated_model):
        expected_nsmap = {"yin": YIN_NAMESPACE, "test": TEST_NAMESPACE}
        assert consolidated_model["nsmap"] == expected_nsmap

    def test_yang_version(self, consolidated_model):
        yang_version = get_nested(consolidated_model, "yang-version", "value")
        assert yang_version == "1"

    def test_namespace(self, consolidated_model):
        namespace = get_nested(consolidated_model, "namespace", "uri")
        assert namespace == TEST_NAMESPACE

    def test_prefix(self, consolidated_model):
        prefix = get_nested(consolidated_model, "prefix", "value")
        assert prefix == "test"

    def test_organization(self, consolidated_model):
        organization = get_nested(consolidated_model, "organization", "text")
        assert organization == "None"

    def test_contact(self, consolidated_model):
        contact = get_nested(consolidated_model, "contact", "text")
        assert contact == "Somebody"

    def test_description(self, consolidated_model):
        description = get_nested(consolidated_model, "description", "text")
        assert (
            description
            == "Test module containing an exhaustive set of possible YANG statements"
        )

    def test_revision(self, consolidated_model):
        date = get_nested(consolidated_model, "revision", "date")
        assert date == "2016-04-22"

        description = get_nested(consolidated_model, "revision", "description", "text")
        assert description == "Initial revision"

    def test_simple_extension_no_arg(self, consolidated_model):
        name = get_nested(consolidated_model, "extension", "name")
        assert name == "simple-extension-no-arg"

        description = get_nested(consolidated_model, "extension", "description", "text")
        assert (
            description
            == "An extension that takes no argument and does not support substatements"
        )

    def test_feature(self, consolidated_model):
        name = get_nested(consolidated_model, "feature", "name")
        assert name == "test-feature"

        description = get_nested(consolidated_model, "feature", "description", "text")
        assert description == "A test feature"


class TestSubmodule(object):
    def test_data_definitions_included(self, consolidated_model):
        name = get_nested(consolidated_model, "container", "name")
        assert name == "submodule-container"


class TestEverything(object):
    """
    Rather than having a dozen tests that each compare one chunk of the consolidated
    model at a time, why not compare the whole thing in one go!
    """

    @pytest.mark.skip(
        "enable this 'test' to automatically re-generate the expected file"
    )
    def test_generate(self, consolidated_model):
        with open(
            os.path.join(os.path.dirname(__file__), "expected.json"), "w"
        ) as file_:
            json.dump(consolidated_model, file_, indent=2)
        assert False

    def test_everything(self, consolidated_model):
        with open(
            os.path.join(os.path.dirname(__file__), "expected.json"), "r"
        ) as file_:
            expected = json.load(file_)

        assert consolidated_model == expected
