# pkgsettings

[![image](https://github.com/kpn/py-pkgsettings/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/kpn/py-pkgsettings/actions/workflows/tests.yml)
[![image](https://img.shields.io/codecov/c/github/kpn-digital/py-pkgsettings/master.svg)](https://codecov.io/github/kpn-digital/py-pkgsettings?branch=master)
[![image](https://img.shields.io/pypi/v/pkgsettings.svg)](https://pypi.org/project/pkgsettings)
[![image](https://img.shields.io/pypi/pyversions/pkgsettings.svg)](https://pypi.org/project/pkgsettings)
[![image](https://readthedocs.org/projects/py-pkgsettings/badge/?version=latest)](https://py-pkgsettings.readthedocs.org/en/latest/?badge=latest)
[![image](https://img.shields.io/pypi/l/pkgsettings.svg)](https://pypi.org/project/pkgsettings)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/kpn/py-pkgsettings)

Easy, generic and extendable way of configuring a package.

## Installation

``` bash
$ pip install pkgsettings
```

## Quickstart with [dataclasses](https://docs.python.org/3/library/dataclasses.html)

### Package code

A configurable package should define a settings dataclass, and a global singleton:

```python
# `your_package/conf.py`

from dataclasses import dataclass
from pkgsettings import Settings


@dataclass
class PackageSettings(Settings):
    hello: str = "World"
    debug: bool = False


settings = PackageSettings()
```

### Application code

The defaults can be changed by their individual attributes:

```python
from your_package.conf import settings

settings.debug = True
```

Or, with the `configure()` method:

```python
from your_package.conf import settings

settings.configure(debug=True, hello="Universe")
```

The `configure()` also supports the positional argument to apply configuration from a different object:

```python
from django.conf import settings as django_settings
from your_package.conf import settings as package_settings

package_settings.configure(django_settings)
```

The `settings` object can be used as context manager:

```python
from your_package.conf import settings

with settings(debug=True):
    assert settings.debug

assert not settings.debug
```

Additionally, you can also use it as a decorator:

```python
from your_package.conf import settings

@settings(debug=True)
def go():
    assert settings.debug

go()

assert not settings.debug
```

## Legacy-style usage

```python
from pkgsettings import Settings

# Create the settings object for your package to use
settings = Settings()

# Now let's define the default settings
settings.configure(hello='World', debug=False)
```

By calling the `configure()` you actually inject a `layer` of settings. When
requesting a setting it will go through all layers until it finds the
requested key.

Now if someone starts using your package it can easily modify the active
settings of your package by calling the configure again.

```python
from my_awesome_package.conf import settings

# Lets change the configuration here
settings.configure(debug=True)
```

Now from within your package you can work with the settings like so:

```python
from conf import settings

print(settings.debug) # This will print: True
print(settings.hello) # This will print: World
```

It is also possible to pass an object instead of kwargs. The settings
object will call `getattr(ur_object, key)` An example below:

```python
class MySettings(object):
    def __init__(self):
        self.debug = True

settings = Settings()
settings.configure(MySettings())
print(settings.debug) # This will print: True
```

## More advanced usage

The settings object can also be used as context manager:

```python
with settings(debug=True):
    print(settings.debug) # This will print: True

print(settings.debug) # This will print: False
```

Additionally, you can also use this as a decorator:

```python
@settings(debug=True)
def go():
    print(settings.debug) # This will print: True

go()

print(settings.debug) # This will print: False
```

## Prefixed Settings

If a group of settings share a common prefix, you can make use of the
`PrefixedSettings` class and pass the desired prefix as an argument,
together with the main settings instance. All attributes will be
automatically prefixed when accessed.

```python
from pkgsettings import PrefixedSettings, Settings

# First create the settings object for your package to use
settings = Settings()

# Suppose some of your settings are all prefixed with 'FOO'
settings.configure(FOO_a='a', FOO_b='b', c='c', debug=False)

# Create a PrefixedSettings instance with the desired prefix
foo_settings = PrefixedSettings(settings, 'FOO_')

foo_settings.a # This will print: a
foo_settings.b # This will print: b

foo_settings.c # This will raise an AttributeError
```
