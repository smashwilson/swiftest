import requests

from .exception import ProtocolError
from .account import Account

class Client:
    """
    The main entry point into Swiftest.

    A Client mediates communications with OpenSwift API endpoints, remembers
    your authentication token throughout the session, and provides access to
    other objects through methods like account() or container().
    """

    def __init__(self, endpoint, username, auth_key):
        """
        Construct a ready-to-use Client.

        Authenticate to the specified OpenSwift endpoint. Remember the generated
        token and storage URL.
        """

        auth_headers = {'X-Auth-User': username, 'X-Auth-Key': auth_key}
        auth_response = requests.get(endpoint, headers=auth_headers)
        auth_response.raise_for_status()

        # Read the storage URL and auth token from the response.
        self.storage_url = auth_response.headers['X-Storage-Url']
        self.auth_token = auth_response.headers['X-Auth-Token']

    def account(self):
        """
        Access metadata about your account.
        """

        return Account(self)

    def _call(self, method, path, **kwargs):
        """
        Perform an HTTP request against the storage endpoint.

        Always include the auth token as a header and add "path" to the storage_url.
        """

        extra = kwargs
        if 'headers' in extra:
            extra['headers']['X-Auth-Token'] = self.auth_token
        else:
            extra['headers'] = {'X-Auth-Token': self.auth_token}
        r = method(self.storage_url + path, **extra)
        r.raise_for_status()
        return r
