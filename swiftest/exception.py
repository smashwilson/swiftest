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
    An unexpected state was encountered in the OpenStack protocol.

    This is raised on many 500 conditions, for example, or cases where expected
    headers are missing from HTTP responses.
    """

class AlreadyExistsError(SwiftestError):
    """
    An attempt is made to create or delete an object or a container that already exists.
    """

class DoesNotExistError(SwiftestError):
    """
    An attempt is made to manipulate an object or a container that does not exist.
    """

    @classmethod
    def _message(cls, tp, name):
        return cls("{0} {1} does not exist.".format(tp, name))

    @classmethod
    def container(cls, container_name):
        return cls._message("Container", container_name)
