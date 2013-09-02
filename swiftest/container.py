import shutil

import requests

from .metadata import Metadata
from .exception import ProtocolError, AlreadyExistsError, DoesNotExistError
from .compat import to_long

class Container:

    _METADATA_ATTRS = ('metadata', 'object_count', 'bytes_used')

    def __init__(self, client, name):
        """
        Construct a Container with a provided name.
        """

        self.name = name
        self.client = client
        self._metadata_fetched = False

    def exists(self):
        try:
            self._fetch_metadata()
            return True
        except DoesNotExistError:
            return False

    def create(self):
        """
        Create a container with this name.

        This method will raise an AlreadyExistsError if the container already
        exists. See create_if_necessary() for a more lenient call.
        """

        r = self._internal_create()
        if r.status_code == 202:
            raise AlreadyExistsError("The container {} already exists.".format(self.name))
        return self

    def create_if_necessary(self):
        """
        Create a container with this name, unless it already exists.

        If the container already exists, this method will be a no-op.
        """

        self._internal_create()
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

        r = self._internal_delete()
        if r.status_code == 404:
            raise DoesNotExistError.container(self.name)
        return self

    def delete_if_necessary(self):
        """
        Delete this container if it exists.
        """

        self._internal_delete()
        return self

    def __getattr__(self, attr_name):
        """
        Resolve this container's metadata properties if necessary.
        """

        if attr_name in Container._METADATA_ATTRS:
            self._fetch_metadata()
            return getattr(self, attr_name)
        else:
            raise AttributeError("Attribute {0} does not exist in a Container.".format(attr_name))

    def __repr__(self):
        return "<Container(name={})>".format(self.name)

    def _fetch_metadata(self):
        """
        Fetch and populate this container's metadata attributes.

        Translate a 404 into a DoesNotExistError.
        """

        def long_header(resp, header_name):
            try:
                return to_long(resp.headers[header_name])
            except ValueError:
                raise ProtocolError("Non-integer received in header {}.".format(header_name))
            except KeyError:
                raise ProtocolError("Missing expected header value {}.}".format(header_name))

        r = self.client._call(requests.head, '/' + self.name, accept_status=[404])
        if r.status_code == 404:
            raise DoesNotExistError.container(self.name)

        self.metadata = Metadata.from_response(self, r, 'Container')
        self.object_count = long_header(r, 'X-Container-Object-Count')
        self.bytes_used = long_header(r, 'X-Container-Bytes-Used')

    def _internal_delete(self):
        """
        Internal deletion method. Use delete() or delete_if_necessary().
        """

        return self.client._call(requests.delete, '/' + self.name, accept_status=[404])

    def _internal_create(self):
        """
        Internal creation method. Use create() or create_if_necessary().
        """

        return self.client._call(requests.put, '/' + self.name)

    def _object_resp(self, name, **kwargs):
        return self.client._call(requests.get, '/{0}/{1}'.format(self.name, name), **kwargs)
