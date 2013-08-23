import requests

from .metadata import Metadata
from .exception import ProtocolError
from .compat import to_long


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
            self.container_count = to_long(meta_response.headers['X-Account-Container-Count'])
            self.bytes_used = to_long(meta_response.headers['X-Account-Bytes-Used'])
        except ValueError:
            raise ProtocolError("Non-integer received in HEAD response.")

        self.metadata = Metadata.from_response(self, meta_response, 'Account')

    def __repr__(self):
        return "<Account(" + repr(self.client) + ")>"
