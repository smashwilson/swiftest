# Swiftest

[![Build Status](https://travis-ci.org/smashwilson/swiftest.png)](https://travis-ci.org/smashwilson/swiftest)

*Swiftest* is a Pythonic API for interacting with OpenSwift object storage providers, built on
[requests](http://docs.python-requests.org/en/latest/).

# Installation

```bash
$ pip install git+https://github.com/smashwilson/swiftest
```

# Usage

```python
>>> from swiftest.client import Client
>>> cli = Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/',
...              username=USER_NAME,
...              auth_key=AUTH_KEY)
<Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/',username='smashwilson',auth_key=...)>
```

## References

 * [OpenSwift v1.0 API](http://docs.openstack.org/api/openstack-object-storage/1.0/content/)
