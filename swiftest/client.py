import requests

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

        if 400 <= auth_response.status_code < 500:
            # Unauthorized.
            raise AuthenticationError(
                "Authentication failed for user {0}. (status: {1})".format(
                    username, auth_response.status_code))
        elif 200 <= auth_response.status_code < 300:
            # Read the storage URL and auth token from the response.
            self.storage_url = auth_response.headers['X-Storage-Url']
            self.auth_token = auth_response.headers['X-Auth-Token']
        else:
            # Unknown status, possibly an internal service error.
            raise SwiftestError(
                "Unexpected status {0} received from authentication server.".format(
                    auth_response.status_code))


class SwiftestError(Exception):
    """
    Root of the hierarchy of exceptions raised by Swiftest.

    Enables bulk catching when desired.
    """

class ProtocolError(SwiftestError):
    """
    An unexpected state was encountered in the OpenSwift protocol.

    This is raised on many 500 conditions, for example, or cases where expected
    headers are missing from HTTP responses.
    """
    pass

class AuthenticationError(SwiftestError):
    """
    Raised when authentication fails or an auth token is rejected.
    """
    pass
