import requests

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

      # Extract metadata from the response.
      self.container_count = long(meta_response.headers['X-Account-Container-Count'])
      self.bytes_used = long(meta_response.headers['X-Account-Bytes-Used'])
