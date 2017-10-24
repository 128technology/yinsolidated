###############################################################################
# Copyright (c) 2016-2017 128 Technology, Inc.
# All rights reserved.
###############################################################################

"""
Pyang plugin that generates a single, consolidated XML representation of a YANG
data model

Usage
=====
pyang -f consolidated <main-module>.yang <augmenting-module>.yang ...

NOTE: the main module MUST be passed as the first positional argument


Output Format
=============

Most YANG statements are simply converted to XML using the rules defined by the
YIN specification. However, the YIN transformation results in one XML document
for each YANG file, and the goal of the the consolidated model is to generate a
single XML document. Thus, the following additional transformations are
performed:


Submodules
----------
All data definitions within a submodule are included as child elements of the
main module element.


Augments
--------

* All augment statements are resolved such that all data definition statements
  within the augment are added as child elements to the element indicated by
  the augment's target node.

* Any when sub-statements of an augment are added as child elements to each of
  the augmenting data definition elements described above. To differentiate
  these from actual when sub-statements of those data definitions, the added
  when elements are given a 'context-node="parent"' attribute. This way, the
  when statement still makes the data definition conditional, and the XPath
  expression can be evaluated against the proper context node.

* Similarly, any if-feature sub-statements of an augment are added as child
  elements to each of the augmenting data definitions. No modifications to
  these elements are necessary because they still make the data definition
  dependant on the feature.

E.g. this YANG snippet:

    container augmented-container;

    augment "augmented-container" {
        if-feature my-feature;
        when "a-leaf != 'foo'";

        container augmenting-container;

        leaf augmenting-leaf {
            type string;
        }
    }

Becomes:

    <container name="augmented-container">
        <container name="augmenting-container">
            <if-feature name="my-feature"/>
            <when condition="a-leaf != 'foo'" context-node="parent"/>
        </container>
        <leaf name="augmenting-leaf">
            <if-feature name="my-feature"/>
            <when condition="a-leaf != 'foo'" context-node="parent"/>
            <type name="string"/>
        </leaf>
    </container>


Uses
----

* All uses statements are resolved such that all data definitions sub-
  statements of the used grouping (grouped data definitions) are added as
  elements in place of the uses statement.

* All when sub-statements of a uses are handled exactly the same way as they
  are for augments, except they are added to the grouped data definition
  elements.

* All if-feature sub-statements of a uses are handled in the same way as they
  are for augments, except they are added to the grouped data definition
  elements.

E.g. this YANG snippet:

    grouping my-grouping {
        if-feature my-feature;
        when "a-leaf != 'foo'";

        container grouped-container;

        leaf grouped-leaf {
            type string;
        }
    }

    container root {
        uses my-grouping;
    }

Becomes:

    <container name="root">
        <container name="grouped-container">
            <if-feature name="my-feature"/>
            <when condition="a-leaf != 'foo'" context-node="parent"/>
        </container>
        <leaf name="grouped-leaf">
            <if-feature name="my-feature"/>
            <when condition="a-leaf != 'foo'" context-node="parent"/>
            <type name="string"/>
        </leaf>
    </container>


Typedefs
--------

Any type statement that refers to a typedef is resolved recursively, such that
the typedef is added as a child element of the type element. The typedef itself
has a child type element, which will also be resolved if it refers to another
typedef.

E.g. this YANG snippet:

    typedef base-type {
        type string {
            length 1..255;
        }
    }

    typedef derived-type {
        type base-type {
            length 10;
        }
    }

    leaf my-leaf {
        type derived-type {
            pattern "[A-Z]*";
        }
    }

Becomes:

    <leaf name="my-leaf>
        <type name="derived-type">
            <pattern value="[A-Z]*"/>
            <typedef name="derived-type">
                <type name="base-type">
                    <length value="10"/>
                    <typedef name="base-type">
                        <type name="string">
                            <length value="1..255"/>
                        </type>
                    </typedef>
                </type>
            </typedef>
        </type>
    </leaf>


Leafrefs
--------

Any leafref type is resolved such that the type statement of the referenced
leaf is added as a child element to the type element. If the referenced leaf's
type is a typedef, it will be resolved as described in the Typedefs section.

E.g. this YANG snippet:

    leaf referenced-leaf {
        type string;
    }

    leaf referring-leaf {
        type leafref {
            path "/referenced-leaf";
        }
    }

Becomes:

    <leaf name="referenced-leaf">
        <type name="string"/>
    </leaf>
    <leaf name="referring-leaf">
        <type name="leafref">
            <path value="/referenced-leaf"/>
            <type name="string"/>
        </type>
    </leaf>


Extensions
----------

Extensions are the only statements not transformed by the rules defined for
YIN. According to the YIN definition, any usage of an extension is added as a
child element of its parent statement, and the argument to the extension
statement can be set as either an attribute on that element, or the text of a
child element. In the consolidated model, any extension statement is simply
added as an element, and its argument is set as the text of that element.

E.g. this YANG snippet:

    namespace "foo:ns";
    prefix foo;

    extension element-ext {
        argument element-arg {
            yin-element true;
        }
    }

    extension attribute-ext {
        argument attribute-arg {
            yin-element false;
        }
    }

    foo:element-ext "Element text";
    foo:attribute-ext "Attribute text";

Becomes:

    <foo:element-ext xmlns:foo="foo:ns">Element text<foo:element-ext>
    <foo:attribute-ext xmlns:foo="foo:ns">Attribute text<foo:attribute-ext>


RPC Input and Output
--------------------

A child element is added for both input and output for an rpc element,
even if the input or output statement was omitted from the rpc definition.

E.g. this YANG snippet:

    rpc my-rpc;

Becomes:

    <rpc name="my-rpc">
        <input/>
        <output/>
    </rpc>


Cases
-----

The case statement can be omitted in YANG if the case only consists of a
single data definition statement. When converted to the consolidated model,
the data definition element will be wrapped in a case element even if the
case statement is omitted.

E.g. this YANG snippet:

    choice my-choice {
        case foo {
            container foo;
        }
        container bar;
    }

Becomes:

    <choice name="my-choice">
        <case name="foo">
            <container name="foo">
        </case>
        <case name="bar">
            <container name="bar">
        </case>
    </choice>


Omitting Resolved Statements
----------------------------

Any statements that are resolved by the above rules become useless in the
consolidated model because the information they convey is represented in-place.
Thus, these statements are NOT added as elements in the consolidated model.

This includes statements with the following keywords:
    * augment
    * belongs-to
    * grouping
    * import
    * include
    * refine
    * submodule
    * uses


Namespaces and Prefixes
-----------------------

Each module has its own local mapping of prefixes to namespaces
for the modules it imports, and text values within the module may use these
locally defined prefixes. Thus, for any given element in the document, it is
also necessary to know the current namespace mapping. This is accomplished by
adding the appropriate namespace mappings to the top-level module element as
well as any augmenting data definitions from external modules.

In addition, each YANG module has its own namespace and associated prefix which
scopes the data definitions contained in that module. When parsing the model,
it is important to know the namespace and prefix to which a data definition
belongs.

To accomplish this, the prefix for the main module is stored as an attribute of
the top-level module element, and the prefix of any modules augmenting the main
module is stored as an attribute of each augmenting data definition element.
This way, any data definition element within the document is scoped to the
prefix of the closest ancestor element with the 'module-prefix' attribute. The
namespace associated with this prefix can be acquired using the namespace
mapping.

E.g. these YANG modules:

    module main {
        namespace "urn:main";
        prefix main;

        container root;
    }

    module augmenting {
        namespace "urn:augmenting";
        prefix aug;

        import main {
            prefix m;
        }

        augment "/m:root" {
            leaf my-leaf {
                types string;
            }
        }
    }

Become:

    <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
            xmlns:main="urn:main"
            name="main"
            module-prefix="main">
        <container name="root">
            <leaf xmlns:aug="urn:augmenting"
                  xmlns:m="urn:main"
                  name="my-leaf"
                  module-prefix="aug">
                <type name="string"/>
            </leaf>
        </container>
    </module>


Identities
----------

Since the consolidated model contains only one module element, identities
defined in other modules are included as children of the module element. In
order to properly represent namespaces, each identity element is given the
namespace map from its original module as well as a 'module-prefix' attribute
to indicate the namespace in which it was defined.

E.g. these YANG modules:

    module main {
        namespace "urn:main";
        prefix main;

        identity base-identity;
    }

    module augmenting {
        namespace "urn:augmenting";
        prefix aug;

        import main {
            prefix m;
        }

        identity derived-identity {
            base m:base-identity;
        }
    }

Become:

    <module xmlns="urn:ietf:params:xml:ns:yang:yin:1"
            xmlns:main="urn:main"
            name="main"
            module-prefix="main">
        <identity xmlns:main="urn:main"
                  module-prefix="main"
                  name="base-identity"/>
        <identity xmlns:aug="urn:augmenting"
                  xmlns:m="urn:main"
                  module-prefix="aug"
                  name="derived-identity">
            <base name="m:base-identity"/>
        </identity>
    </module>
"""

from __future__ import unicode_literals

from lxml import etree
from pyang import plugin, statements, syntax, yin_parser


_DATA_DEFINITION_KEYWORDS = ['container', 'leaf', 'leaf-list', 'list',
                             'choice', 'case', 'augment', 'uses', 'anyxml']

_EXTRA_PYANG_DATA_KEYWORDS = ['notification', 'rpc', 'input', 'output']

_RESOLVED_KEYWORDS = ['grouping', 'import', 'include', 'typedef']

_DATA_KEYWORDS = (_DATA_DEFINITION_KEYWORDS +
                  _EXTRA_PYANG_DATA_KEYWORDS +
                  _RESOLVED_KEYWORDS)


def pyang_plugin_init():
    """Required function definition for Pyang to register the plugin"""

    plugin.register_plugin(ConsolidatedModelPlugin())


class ConsolidatedModelPlugin(plugin.PyangPlugin):

    """The plugin class to register with Pyang"""

    def add_output_format(self, formats):
        self.multiple_modules = True
        formats['consolidated'] = self

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

    if _is_augmenting(statement):
        _append_when_elements_from_augment(statement.i_augment, yin_element)

    if _is_member_of_grouping(statement):
        _append_if_feature_elements_from_uses(statement.i_uses, yin_element)
        _append_when_elements_from_uses(statement.i_uses, yin_element)

    if statement.keyword == 'type':
        _append_children_for_type(statement, yin_element)

    if hasattr(statement, 'i_children'):
        for data_definition in statement.i_children:
            _make_yin_element_recursive(data_definition, yin_element)


def _iterate_non_data_sub_statements(statement):
    for sub_statement in statement.substmts:
        if sub_statement.keyword not in _DATA_KEYWORDS:
            yield sub_statement


def _append_when_elements_from_augment(augment_statement, yin_element):
    when_statements = augment_statement.search('when')
    _append_when_elements_with_parent_context(when_statements, yin_element)


def _append_when_elements_with_parent_context(when_statements, yin_element):
    for when_statement in when_statements:
        when_element = _make_builtin_yin_element(when_statement, yin_element)
        when_element.set('context-node', 'parent')


def _is_member_of_grouping(statement):
    return (statement.keyword in _DATA_DEFINITION_KEYWORDS and
            hasattr(statement, 'i_uses') and
            statement.i_uses is not None)


def _append_if_feature_elements_from_uses(uses_statements, yin_element):
    for uses_statement in uses_statements:
        for if_feature_statement in uses_statement.search('if-feature'):
            _make_builtin_yin_element(if_feature_statement, yin_element)


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
