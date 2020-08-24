# Copyright 2017 128 Technology, Inc.

"""YINsolidated package"""

# pylint: disable=wildcard-import,unused-wildcard-import

# Forward module definitions
from yinsolidated._error import (
    Error,
    MissingIdentityError,
    MissingModuleNameError,
    MissingPrefixError,
)
from yinsolidated._version import __version__
from yinsolidated.json_parser import parse as parse_json
from yinsolidated.parser import *
