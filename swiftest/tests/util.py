"""
Unit testing utility functions.
"""

import httpretty

from swiftest.client import Client

AUTH_TOKEN='faketoken'
STORAGE_URL='https://storage.endpoint.com/v1/me'

def create_client():
    """
    Mock the authentication endpoint to create a Client object.

    Assumes that httpretty is already enabled.
    """

    httpretty.register_uri(httpretty.GET, 'https://auth.endpoint.com/v1/', status=204,
        x_auth_token=AUTH_TOKEN,
        x_storage_url=STORAGE_URL)

    return Client(endpoint='https://auth.endpoint.com/v1/',
        username='me', auth_key='swordfish')
