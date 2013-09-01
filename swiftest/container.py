import shutil

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

    def download_string(self, name, encoding=None):
        """
        Download the contents of a named object to a String.

        By default, the String's encoding will be inferred from header information by the
        underlying requests call, overridden by an explicit encoding if one is provided.
        """

        resp = self._object_resp(name)
        if encoding:
            resp.encoding = encoding
        return resp.text

    def download_binary(self, name):
        """
        Download the contents of a named object as uninterpreted binary.
        """

        return self._object_resp(name).content

    def download_file(self, name, io, buffer_size=None):
        """
        Download the contents of a named object to an open file-like destination.

        Provide a custom buffer size to override the default copy buffer provided by shutils. Be sure
        that "io" is opened in binary mode if this object contains binary data, to avoid newline
        translation or other encoding hiccups.

        Opening and closing "io" is the caller's responsibility.
        """
        resp = self._object_resp(name, stream=True)
        shutil.copyfileobj(resp.raw, io, buffer_size)

    def delete(self):
        self.client._call(requests.delete, '/' + self.name)

    def __repr__(self):
        return "<Container(name={})>".format(self.name)

    def _object_resp(self, name, **kwargs):
        return self.client._call(requests.get, '/{0}/{1}'.format(self.name, name), **kwargs)

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

    def __repr__(self):
        return "<NullContainer(name={})>".format(self.name)
