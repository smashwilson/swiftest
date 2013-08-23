import re
import requests

from .metadata import Metadata
from .exception import ProtocolError
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

    def _commit_metadata(self, metadata):
        """
        Create, update or delete container metadata based on the changes made to
        the metadata dictionary.
        """
        h = {}
        for update in metadata.updates:
            h["X-Container-Meta-" + update] = metadata[update]
        for deletion in metadata.deletions:
            h["X-Container-Meta-" + deletion] = ''
        self.client._call(requests.post, '', headers=h)
