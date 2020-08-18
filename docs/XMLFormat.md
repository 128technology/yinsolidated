# YINsolidated Format

Most YANG statements are simply converted to XML using the rules defined by the
YIN specification. However, the YIN transformation results in one XML document
for each YANG file, and the goal of the the **YINsolidated** model is to
generate a single XML document. Thus, the following additional transformations
are performed:

## Submodules

All data definitions within a `submodule` are included as child elements of the
main module element.

## Augments

* All `augment` statements are resolved such that all data definition statements
  within the `augment` are added as child elements to the element indicated by
  the `augment`'s target node.

* Any `when` sub-statements of an `augment` are added as child elements to each
  of the augmenting data definition elements described above. To differentiate
  these from actual `when` sub-statements of those data definitions, the added
  `when` elements are given a `context-node="parent"` attribute. This way, the
  `when` statement still makes the data definition conditional, and the XPath
  expression can be evaluated against the proper context node.

* Similarly, any `if-feature` sub-statements of an `augment` are added as child
  elements to each of the augmenting data definitions. No modifications to
  these elements are necessary because they still make the data definition
  dependent on the feature.

E.g. this YANG snippet:

```yang
container augmented-container;

augment "augmented-container" {
    if-feature my-feature;
    when "a-leaf != 'foo'";

    container augmenting-container;

    leaf augmenting-leaf {
        type string;
    }
}
```

Becomes:

```xml
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
```

## Uses

* All `uses` statements are resolved such that all data definitions sub-
  statements of the used `grouping` (grouped data definitions) are added as
  elements in place of the `uses` statement.

* All `when` sub-statements of a `uses` are handled exactly the same way as
  those of an `augment`, except they are added to the grouped data definition
  elements.

* All `if-feature` sub-statements of a `uses` are handled in the same way as
  those of an `augment`, except they are added to the grouped data
  definition elements.

E.g. this YANG snippet:

```yang
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
```

Becomes:

```xml
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
```

## Typedefs

Any `type` statement that refers to a `typedef` is resolved recursively, such
that the `typedef` is added as a child element of the `type` element. The
`typedef` itself has a child `type` element, which will also be resolved if it
refers to another `typedef`.

E.g. this YANG snippet:

```yang
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
```

Becomes:

```xml
<leaf name="my-leaf">
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
```

## Leafrefs

Any `leafref` type is resolved such that the `type` statement of the referenced
`leaf` is added as a child element to the `type` element. If the type of the
referenced `leaf` is a `typedef`, it will be resolved as described in the
[Typedefs](#typedefs) section.

E.g. this YANG snippet:

```yang
leaf referenced-leaf {
    type string;
}

leaf referring-leaf {
    type leafref {
        path "/referenced-leaf";
    }
}
```

Becomes:

```xml
<leaf name="referenced-leaf">
    <type name="string"/>
</leaf>
<leaf name="referring-leaf">
    <type name="leafref">
        <path value="/referenced-leaf"/>
        <type name="string"/>
    </type>
</leaf>
```

## Extensions

`extension` statements can be represented in the **YINsolidated** model in two different ways.

### Simple Extensions

This is the default format, which provides a simplified representation over the traditional YIN format. Each `extension` statement is simply added as a child element of its parent statement, and its argument is set as the text of that element.

E.g. this YANG snippet:

```yang
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
foo:attribute-ext "Attribute text" {
    description "This won't appear in YINsolidated";
}
```

Becomes:

```xml
<foo:element-ext xmlns:foo="foo:ns">Element text<foo:element-ext>
<foo:attribute-ext xmlns:foo="foo:ns">Attribute text<foo:attribute-ext>
```

### Complex (YIN-formatted) Extensions

The simple format does not support sub-statements on extensions. To support this use case, the traditional YIN format can be enabled by adding the tag `#yinformat` to the extension description.

In this format, each `extension` statement is added as a child element of its parent statement, and its argument can be set either as an attribute on that element or as a child element.

E.g. this YANG snippet:

```yang
namespace "foo:ns";
prefix foo;

extension element-ext {
    argument element-arg {
        yin-element true;
    }
    description "This should follow #yinformat";
}

extension attribute-ext {
    argument attribute-arg {
        yin-element false;
    }
    description "This should follow #yinformat";
}

foo:element-ext "Element text";
foo:attribute-ext "Attribute text" {
    description "This will appear in YINsolidated";
}
```

Becomes:

```xml
<foo:element-ext xmlns:foo="foo:ns">
    <foo:element-arg>Element text</foo:element-arg>
<foo:element-ext>
<foo:attribute-ext xmlns:foo="foo:ns" attribute-arg="Attribute text">
    <description>This will appear in YINsolidated</description>
<foo:attribute-ext>
```

## RPC Input and Output

Both an `input` child element and an `output` child element are added to each
`rpc` element, even if the `input` or `output` statement was omitted from the
`rpc` definition.

E.g. this YANG snippet:

```yang
rpc my-rpc;
```

Becomes:

```xml
<rpc name="my-rpc">
    <input/>
    <output/>
</rpc>
```

## Cases

The `case` statement can be omitted in YANG if the `case` only consists of a
single data definition statement. When converted to the **YINsolidated** model,
this data definition element will be wrapped in a `case` element even if the
`case` statement is omitted.

E.g. this YANG snippet:

```yang
choice my-choice {
    case foo {
        container foo;
    }
    container bar;
}
```

Becomes:

```xml
<choice name="my-choice">
    <case name="foo">
        <container name="foo">
    </case>
    <case name="bar">
        <container name="bar">
    </case>
</choice>
```

## Omitting Resolved Statements

Any statements that are resolved by the above rules become useless in the
**YINsolidated** model because the information they convey is represented in-
place. Thus, the following statements are **NOT** added as elements in the
**YINsolidated** model:

* `augment`
* `belongs-to`
* `grouping`
* `import`
* `include`
* `refine`
* `submodule`
* `uses`

## Namespaces and Prefixes

Each module has its own local mapping of prefixes to namespaces for the modules
it imports, and text values within the module may use these locally defined
prefixes. Thus, for any given element in the document, it is also necessary to
know the current namespace mapping. This is accomplished by adding the
appropriate namespace mappings to the top-level `module` element as well as to
any augmenting data definitions from external modules.

In addition, each YANG module has its own namespace and associated prefix which
scopes the data definitions contained in that module. When parsing the model, it
is important to know the namespace and prefix to which a data definition
belongs.

To accomplish this, the prefix for the main module is stored as an attribute of
the top-level module element, and the prefix of any module augmenting the main
module is stored as an attribute of each augmenting data definition element.
This way, any data definition element within the document is scoped to the
prefix of the closest ancestor element with the `module-prefix` attribute. The
namespace associated with this prefix can be acquired using the namespace
mapping.

E.g. these YANG modules:

```yang
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
```

Become:

```xml
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
```

## Identities

Since the **YINsolidated** model contains only one module element, `identity`
statements defined in other modules are included as children of the module
element. In order to properly represent namespaces, each identity element is
given the namespace map from its original module as well as a `module-prefix`
attribute to indicate the namespace in which it was defined.

E.g. these YANG modules:

```yang
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
```

Become:

```xml
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
```
