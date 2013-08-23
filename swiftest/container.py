import requests

from .metadata import Metadata
from .exception import ProtocolError, AlreadyExistsError
from .compat import to_long

class Container:

    def __init__(self, client, name):
        """
        Acquire basic Container metadata.

        An HTTPNotFoundError will be raised if the container does not exist.
        """

        self.name = name
        self.client = client

        meta_response = self.client._call(requests.head, '/' + name)

        try:
            self.object_count = to_long(meta_response.headers['X-Container-Object-Count'])
            self.bytes_used = to_long(meta_response.headers['X-Container-Bytes-Used'])
        except ValueError:
            raise ProtocolError("Non-integer received in container HEAD request.")

        self.metadata = Metadata.from_response(self, meta_response, 'Container')

    def exists(self):
        return True

    def create(self):
        raise AlreadyExistsError("Container {0} already exists.".format(self.name))

    def create_if_necessary(self):
        return self

class NullContainer:
    """
    A container that doesn't exist (yet).
    """

    def __init__(self, client, name):
        self.name = name
        self.client = client

    def exists(self):
        return False

    def create(self):
        """
        Create a container with this name.

        An HTTPError will be raised if the container already exists at this
        point (by a race condition). The newly created Container will be
        returned.
        """

        self.client._call(requests.put, '/' + self.name)
        return Container(self.client, self.name)

    def create_if_necessary(self):
        return create()
