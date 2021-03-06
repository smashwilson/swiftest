# Swiftest

[![Build Status](https://travis-ci.org/smashwilson/swiftest.png)](https://travis-ci.org/smashwilson/swiftest)

*Swiftest* is a Pythonic API for interacting with OpenStack Swift object storage providers, built on
[requests](http://docs.python-requests.org/en/latest/).

## Installation

```bash
$ pip install git+https://github.com/smashwilson/swiftest
```

## Usage

Most interaction with Swiftest begins by creating a Client, initialized with your credentials:

```python
>>> from swiftest.client import Client
>>> cli = Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/',
...              username=USER_NAME,
...              auth_key=AUTH_KEY)
<Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/',username='smashwilson',auth_key=...)>
```

### Accounts

Query or update your account metadata by acquiring an `Account` object from your `Client`. Arbitrary metadata
can be managed by manipulating the `.metadata` dictionary. Save your changes by calling its `save()` method.

```python
>>> account = cli.account()
<Account(Client(endpoint='https://identity.api.rackspacecloud.com/v1.0/',username='smashwilson',auth_key=...))>
>>> account.metadata['NewKey'] = 'SomeValue'
>>> del account.metadata['ExistingKey']
>>> account.metadata.save()
```

### Containers

Get `Container` objects from a `Client` by calling its `container()` method. If no container with the specified name
exists yet, a `NullContainer` will be returned instead. You can determine which you have by calling `exists()` on the
returned object. Create a new `Container` by calling `create()` or `create_if_necessary()`.

```python
>>> existing = cli.container('existing')
<Container(name=existing)>
>>> if existing.exists():
...    print("Got a reference to the existing container.")
Got a reference to the existing container.
>>> notyet = cli.container('notyet')
<NullContainer(name=notyet)>
>>> notyet.create()
<Container(name=notyet)>
>>> ondemand = cli.container('ondemand').create_if_necessary()
<Container(name=ondemand)>
```

Existing containers can be acquired from `Client`'s `containers()` generator method.

```python
>>> for c in cli.containers():
...    print("Got existing container: ", c.name)
Got existing container: foo
Got existing container: bar
Got existing container: baz
```

## References

 * [OpenStack Object Storage v1.0 API](http://docs.openstack.org/api/openstack-object-storage/1.0/content/)
