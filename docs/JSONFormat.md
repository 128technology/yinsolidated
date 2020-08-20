# YINsolidated Format

The goal of YINsolidated is to generate a single JSON document with all augments and
submodules merged together. Because the native `yin` format is XML there are some
oddities when converting to JSON.

What would be a XML node becomes a JSON Object that represents a single `YinElement`
with the following schema:

- Each object always has a `"keyword": string`. This would be the XML element tag.
- Sub-objects are grouped under `"children": YinElement[]`.
- Each object has `namespace: string`
- Each object has `nsmap: { [prefix: string]: string }` which is a mapping of namespace-prefix to uri
- All other attributes are optional.

Additionally the following transformations are applied:

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

```json
{
  "keyword": "container",
  "name": "augmented-container",
  "children": [
    {
      "keyword": "container",
      "name": "augmenting-container",
      "children": [
        { "keyword": "if-feature", "name": "my-feature" },
        { "keyword": "when", "condition": "a-leaf != 'foo'", "context-node": "parent" }
      ]
    },
    {
      "keyword": "leaf",
      "name": "augmenting-leaf",
      "children": [
        { "keyword": "if-feature", "name": "my-feature"},
        { "keyword": "when", "condition": "a-leaf != 'foo'", "context-node": "parent" }
        { "keyword": "type", "name": "string" }
      ]
    }
  ]
}
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

```json
{
  "keyword": "root",
  "name": "grouped-container",
  "children": [
    {
      "keyword": "container",
      "name": "grouped-container",
      "children": [
        { "keyword": "if-feature", "name": "my-feature" },
        { "keyword": "when", "condition": "a-leaf != 'foo'", "context-node": "parent" }
      ]
    },
    {
      "keyword": "leaf",
      "name": "grouped-leaf",
      "children": [
        { "keyword": "if-feature", "name": "my-feature"},
        { "keyword": "when", "condition": "a-leaf != 'foo'", "context-node": "parent" }
        { "keyword": "type", "name": "string" }
      ]
    }
  ]
}
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

```json
{
  "keyword": "leaf",
  "name": "my-leaf",
  "children": [
    {
      "keyword": "type",
      "name": "derived-type",
      "children": [
        { "keyword": "pattern", "value": "[A-Z]*" },
        {
          "keyword": "typedef",
          "name": "derived-type",
          "children": [
            {
              "keyword": "type",
              "name": "base-type",
              "children": [
                { "keyword": "length", "value": "10" },
                {
                  "keyword": "typedef",
                  "name": "base-type",
                  "children": [
                    {
                      "keyword": "type",
                      "name": "string",
                      "children": [{ "keyword": "length", "value": "1..255" }]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
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

```json
{
  "keyword": "leaf",
  "name": "referenced-string",
},
{
  "keyword": "leaf",
  "name": "referring-leaf",
  "children": [
    {
      "keyword": "type",
      "name": "leafref",
      "children": [
        { "keyword": "path", "value": "/referenced-leaf" },
        { "keyword": "type", "name": "string" },
      ]
    }
  ]
}
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

```json
{
    "keyword": "element-ext",
    "namespace": "foo:ns",
    "nsmap": { "foo": "foo:ns" },
    "text": "Element text"
},
{
    "keyword": "attribute-ext",
    "namespace": "foo:ns",
    "nsmap": { "foo": "foo:ns" },
    "text": "Attribute text"
}
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

```json
{
    "keyword": "element-ext",
    "namespace": "foo:ns",
    "nsmap": { "foo": "foo:ns" },
    "text": "Element text"
},
{
    "keyword": "attribute-ext",
    "namespace": "foo:ns",
    "nsmap": { "foo": "foo:ns" },
    "attribute-arg": "Attribute text",
    "children": [{ "keyword": "description", "text": "This will appear in YINsolidated" }]
}
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

```json
{
  "keyword": "choice",
  "name": "my-choice",
  "children": [
    {
      "keyword": "case",
      "name": "foo",
      "children": [{ "keyword": "container", "name": "foo" }]
    },
    {
      "keyword": "case",
      "name": "bar",
      "children": [{ "keyword": "container", "name": "bar" }]
    }
  ]
}
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

```json
{
  "keyword": "module",
  "name": "main",
  "module-prefix": "main",
  "namespace": "urn:main",
  "nsmap": { "main": "urn:main", "yin": "urn:ietf:params:xml:ns:yang:yin:1" },
  "children": [
    {
      "keyword": "container",
      "name": "root",
      "children": [
        {
          "keyword": "leaf",
          "name": "my-leaf",
          "module-prefix": "aug",
          "namespace": "urn:augmenting",
          "nsmap": { "m": "urn:main", "yin": "urn:ietf:params:xml:ns:yang:yin:1" },
          "children": [{ "keyword": "type", "name": "string" }]
        },
      ]
    }
  ]
}
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

```json
{
  "keyword": "module",
  "name": "main",
  "module-prefix": "main",
  "namespace": "urn:main",
  "nsmap": { "main": "urn:main", "yin": "urn:ietf:params:xml:ns:yang:yin:1" },
  "children": [
    {
      "keyword": "identity",
      "name": "base-identity",
      "module-prefix": "main",
      "namespace": "urn:main",
      "nsmap": { "main": "urn:main", "yin": "urn:ietf:params:xml:ns:yang:yin:1" },
    },
    {
      "keyword": "identity",
      "name": "derived-identity",
      "module-prefix": "aug",
      "namespace": "urn:augmenting",
      "nsmap": { "m": "urn:main", "yin": "urn:ietf:params:xml:ns:yang:yin:1", "aug": "url:augmenting" },
      "children": [{ "keyword": "base", "name": "m:base-identity" }]
    }
  ]
}
```
