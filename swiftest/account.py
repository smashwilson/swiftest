import re
import requests

from .metadata import Metadata
from .exception import ProtocolError

import sys
if sys.version > '3':
    # int is long in Python 3 (long doesn't exist)
    long = int

class Account:
    """
    Report basic account metadata.
    """

    def __init__(self, client):
        self.client = client

        # Perform a HEAD request against the storage endpoint to fetch basic
        # account metadata.
        meta_response = self.client._call(requests.head, '')

        try:
            # Extract metadata from the response.
            self.container_count = long(meta_response.headers['X-Account-Container-Count'])
            self.bytes_used = long(meta_response.headers['X-Account-Bytes-Used'])
        except ValueError:
            raise ProtocolError("Non-integer received in HEAD response.")

        self.metadata = Metadata.from_response(self, meta_response, 'Account')

    def _commit_metadata(self, metadata):
        """
        Create, update or delete account metadata based on the changes made to
        the metadata dictionary.
        """
        h = {}
        for update in metadata.updates:
            h["X-Account-Meta-" + update] = metadata[update]
        for deletion in metadata.deletions:
            h["X-Account-Meta-" + deletion] = ''
        self.client._call(requests.post, '', headers=h)

    def __repr__(self):
        return "<Account(" + repr(self.client) + ")>"
