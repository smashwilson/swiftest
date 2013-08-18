"""
Exception classes used throughout the Swiftest library.
"""

class SwiftestError(Exception):
    """
    Root of the hierarchy of exceptions raised by Swiftest.

    Enables bulk catching when desired.
    """

class ProtocolError(SwiftestError):
    """
    An unexpected state was encountered in the OpenSwift protocol.

    This is raised on many 500 conditions, for example, or cases where expected
    headers are missing from HTTP responses.
    """
    pass

class AuthenticationError(SwiftestError):
    """
    Raised when authentication fails or an auth token is rejected.
    """
    pass
