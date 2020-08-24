# Copyright 2020 128 Technology, Inc.

"""Define all the exceptions of yinsolidated."""


class Error(Exception):
    """Base exception for yinsolidated."""


class _MissingAttributeError(Error):

    """Could not find an attribute"""

    def __init__(self, attr, data_def_element):
        message = "No {} attribute found for ancestors of {} '{}'".format(
            attr, data_def_element.keyword, data_def_element.name
        )
        super(_MissingAttributeError, self).__init__(message)


class MissingPrefixError(_MissingAttributeError):

    """Could not find prefix attribute"""

    def __init__(self, data_def_element):
        super(MissingPrefixError, self).__init__("prefix", data_def_element)


class MissingModuleNameError(_MissingAttributeError):

    """Could not find module-name attribute"""

    def __init__(self, data_def_element):
        super(MissingModuleNameError, self).__init__("module-name", data_def_element)


class MissingNamespaceError(_MissingAttributeError):

    """Could not find namespace attribute"""

    def __init__(self, data_def_element):
        super(MissingNamespaceError, self).__init__("namespace", data_def_element)


class MissingIdentityError(Error):
    def __init__(self, name, namespace):
        super(MissingIdentityError, self).__init__(
            "Could not find identity {} in namespace {}".format(name, namespace)
        )
