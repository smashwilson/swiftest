import shutil

import requests

from .metadata import Metadata
from .exception import ProtocolError, AlreadyExistsError, DoesNotExistError
from .compat import to_long

class Container:

    _DELEGATED_ATTRS = ('metadata', 'object_count', 'bytes_used')

    def __init__(self, client, name):
        """
        Acquire basic Container metadata.

        An HTTPNotFoundError will be raised if the container does not exist.
        """

        self.name = name
        self.client = client
        self.internal = None

    def exists(self):
        return self._internal().exists()

    def create(self):
        """
        Create a container with this name.

        This method will raise an AlreadyExistsError if the container already
        exists. See create_if_necessary() for a more lenient call.
        """

        self._internal().create()
        self._resolve()
        return self

    def create_if_necessary(self):
        """
        Create a container with this name, unless it already exists.

        If the container already exists, this method will be a no-op.
        """

        self._internal().create_if_necessary()
        self._resolve()
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
        """
        Delete this container.

        Raises a DoesNotExistError if this container doesn't exist to be
        deleted. Use delete_if_necessary() for a more lenient deletion.
        """

        self._internal().delete()
        self.internal = NullContainer(self.client, self.name)

    def __getattr__(self, attr_name):
        """
        Resolve this container's internal representation before permitting attribute access.
        """

        if attr_name in Container._DELEGATED_ATTRS:
            return getattr(self._internal(), attr_name)
        else:
            return super.__getattr__(attr_name)

    def __repr__(self):
        if self.internal:
            exists = self.internal.exists()
        else:
            exists = '?'
        return "<Container(name={}, exists={})>".format(self.name, exists)

    def _internal(self):
        """
        Lazily construct the currently appropriate internal reprentation.
        """

        if self.internal:
            return self.internal
        else:
            return self._resolve()

    def _resolve(self):
        """
        Force instantiation of our internal representation.

        Populates "internal" with either an ExistingContainer or a NullContainer,
        fetching container metadata in the process. Raises an HTTPError if an
        unexpected HTTP error condition is encountered.
        """

        try:
            meta_response = self.client._call(requests.head, '/' + self.name)

            # If no HTTPError was raised, the container exists.
            self.internal = ExistingContainer(self.client, self.name, meta_response)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # If a 404 was encountered, the container does not exist.
                self.internal = NullContainer(self.client, self.name)
            else:
                raise

        return self.internal

    def _object_resp(self, name, **kwargs):
        return self.client._call(requests.get, '/{0}/{1}'.format(self.name, name), **kwargs)

class ExistingContainer:
    """
    A Container that exists.

    Clients should not interact with this class directly; use the more friendly Container wrapper
    instead. This is an internal representation that may be swapped with a NullContainer as various
    operations are performed.
    """

    def __init__(self, client, name, meta_response):
        self.client = client
        self.name = name

        try:
            self.object_count = to_long(meta_response.headers['X-Container-Object-Count'])
            self.bytes_used = to_long(meta_response.headers['X-Container-Bytes-Used'])
        except ValueError:
            raise ProtocolError("Non-integer received in container HEAD request.")

        self.metadata = Metadata.from_response(self, meta_response, 'Container')

    def exists(self):
        return True

    def create(self):
        """
        It's an error to attempt to create a container that already exists.

        Use create_if_necessary() instead to create containers lazily.
        """
        raise AlreadyExistsError("Container {0} already exists.".format(self.name))

    def create_if_necessary(self):
        """
        No-op for existing containers.
        """
        pass

    def delete(self):
        self.client._call(requests.delete, '/' + self.name)

    def __repr__(self):
        return "<ExistingContainer(name={})>".format(self.name)

class NullContainer:
    """
    A container that doesn't exist (yet).

    Clients should not interact with this class directly; use the more friendly Container wrapper
    instead. This is an internal representation that may be swapped seamlessly with an ExistingContainer
    as operations are performed.
    """

    def __init__(self, client, name):
        self.client = client
        self.name = name

    def exists(self):
        return False

    def create(self):
        """
        Create a container with this name.

        An HTTPError will be raised if the container already exists at this
        point (by a race condition).
        """

        self.client._call(requests.put, '/' + self.name)

    def create_if_necessary(self):
        self.create()

    def delete(self):
        raise DoesNotExistError.container(self.name)

    def __getattr__(self, attr):
        if attr in Container._DELEGATED_ATTRS:
            raise DoesNotExistError.container(self.name)
        else:
            super.__getattr__(attr)

    def __repr__(self):
        return "<NullContainer(name={})>".format(self.name)
