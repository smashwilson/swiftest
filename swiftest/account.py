import requests

from .exception import AuthenticationError, ProtocolError
from .compat import to_long

class Account:
    """
    Report basic account metadata.
    """

    def __init__(self, client):
        self.client = client

        # Perform a HEAD request against the storage endpoint to fetch basic
        # account metadata.
        meta_response = requests.head(client.storage_url,
            headers={'X-Auth-Token': client.auth_token})

        if 200 <= meta_response.status_code < 300:
            # Extract metadata from the response.
            self.container_count = to_long(meta_response.headers['X-Account-Container-Count'])
            self.bytes_used = to_long(meta_response.headers['X-Account-Bytes-Used'])
        elif 400 <= meta_response.status_code < 500:
            raise AuthenticationError(
                "Auth token {0} was rejected.".format(client.auth_token))
        else:
            raise ProtocolError(
                "Unexpected status {0} received from the storage endpoint.".format(
                    meta_response.status_code))
