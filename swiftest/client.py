import requests

from .exception import ProtocolError
from .account import Account
from .container import Container

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

        self.endpoint = endpoint
        self.username = username

        auth_headers = {'X-Auth-User': username, 'X-Auth-Key': auth_key}
        auth_response = requests.get(self.endpoint, headers=auth_headers)
        auth_response.raise_for_status()

        # Read the storage URL and auth token from the response.
        self.storage_url = auth_response.headers['X-Storage-Url']
        self.auth_token = auth_response.headers['X-Auth-Token']

    def account(self):
        """
        Access metadata about your account.
        """

        return Account(self)

    def container(self, name):
        """
        Access a Container within this account by name.

        If no container with this name exists, a NullContainer will be
        returned instead.
        """

        try:
            return Container(self, name)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return NullContainer(self, name)
            else:
                raise

    def container_names(self):
        """
        List the names of Containers available in this account.
        """

        names = self._call(requests.get, '').text.split("\n")
        return [name for name in names if name.strip()]

    def containers(self):
        """
        Generate each existing Container.
        """

        for name in self.container_names():
            yield self.container(name)

    def _call(self, method, path, accept_status=[], **kwargs):
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
        if r.status_code not in accept_status:
            r.raise_for_status()
        return r

    def __repr__(self):
        cli_str = "<Client(endpoint='{}',username='{}',auth_key={})>"
        return cli_str.format(self.endpoint,
                              self.username,
                              "...")
