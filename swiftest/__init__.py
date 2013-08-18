"""
Pythonic client for OpenSwift.

>>> from client import Client
>>> cli = Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/', username=USER_NAME, auth_key=AUTH_KEY)
"""

__all__ = ['VERSION']

# Version string for Swiftest. Follows rational versioning in "major.minor.path" format.
# MAJOR: Incremented when the exported public API is changed in a backwards-incompatible way.
# MINOR: Incremented when the public API has backwards-compatible changes.
# PATCH: Incremented for internal bugfixes.
VERSION='1.0.0'

from . import account
from . import client
from . import exception
from . import metadata
