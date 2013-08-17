"""
Pythonic client for OpenSwift.
"""

__all__ = ['VERSION']

# Version string for Swiftest. Follows rational versioning in "major.minor.path" format.
# MAJOR: Incremented when the exported public API is changed in a backwards-incompatible way.
# MINOR: Incremented when the public API has backwards-compatible changes.
# PATCH: Incremented for internal bugfixes.
VERSION='1.0.0'

# Export Client, the primary entry point into swiftest.
from client import Client
