# YINsolidated [![Build Status](https://travis-ci.org/128technology/yinsolidated.svg?branch=master)](https://travis-ci.org/128technology/yinsolidated)

## Overview
**YINsolidated** is a YIN-like representation of a YANG model, consolidated into a single XML file.

While YIN is easier to programmatically consume than YANG, simply because it's XML, it's still just a one-for-one mapping from YANG, which leaves a significant amount of parsing logic up to the consumer. An application that consumes YIN files needs to resolve `uses` statements, `augment` statements, `typedef`s, `identityref`s, `leafref`s, and more.

**YINsolidated** takes care of all of that overhead for you, providing you with a single XML file representing your entire model.

## What this package provides
* A `pyang` plugin for generating a **YINsolidated** model from a YANG model consisting of one or more YANG modules
* A Python library for parsing the **YINsolidated** model into an in-memory XML document with convenient YANG-specific methods and properties layered on top of the elements

## Installation
```
$ pip install yinsolidated
```
To generate a **YINsolidated** module, you will need to install `pyang` separately:
```
$ pip install pyang
```

## Generating a YINsolidated model
### With pyang >= 1.7.2
The **YINsolidated** plugin will be automatically recognized by `pyang` by way of `setuptools` entry points, so you simply need to invoke `pyang` with the `yinsolidated` format:
```
$ pyang -f yinsolidated -o yinsolidatedModel.xml main-module.yang other-module.yang ...
```
**NOTE:** The main YANG module (the one that includes other submodules or is augmented by other modules) needs to be passed as the first positional argument.
### With pyang < 1.7.2
This version of `pyang` does not yet have support for the `setuptools` entry point, so the path in which the plugin is installed must be explicitly passed to the `pyang` command:
```
$ export PLUGINDIR=`/usr/bin/env python -c \
    'import os; from yinsolidated.plugin import plugin; \
    print os.path.dirname(plugin.__file__)'`
$ pyang --plugindir $PLUGINDIR -f yinsolidated -o yinsolidatedModel.xml main-module.yang other-module.yang ...
```

## Parsing a YINsolidated model
### From a file
```python
import yinsolidated

model_tree = yinsolidated.parse('yinsolidatedModel.xml')
```
### From a string
```python
import yinsolidated

with open('yinsolidatedModel.xml') as model_file:
    model_string = model_file.read()

model_tree = yinsolidated.fromstring(model_string)
```

## Documentation
[The YINsolidated Format](docs/Format.md)
