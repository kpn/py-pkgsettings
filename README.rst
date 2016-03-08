pkgsettings
===========

[![build-status-image]][travis]
[![coverage-status-image]][codecov]
[![pypi-version]][pypi]

Goal
----

The goal of this package is to offer an easy, generic and extendable way
of configuring a package.

Installation
------------

.. code-block:: bash

    $ pip install pkgsettings

Usage
-----

.. code-block:: python

    from pkgsettings import Settings

    # Create the settings object for your package to use
    settings = Settings()

    # Now lets defined the default settings
    settings.configure(hello='World', debug=False)

By calling the configure you actually inject a `layer` of settings.
When requesting a setting it will go through all layers until it finds the
requested key.

Now if someone starts using your package it can easily modify the active
settings of your package by calling the configure again.

.. code-block:: python

    from my_awesome_package.conf import settings

    # Lets change the configuration here
    settings.configure(debug=True)


Now from within your package you can work with the settings like so:

.. code-block:: python

    from conf import settings

    print(settings.debug) # This will print: True
    print(settings.hello) # This will print: World



[build-status-image]: https://secure.travis-ci.org/kpn-digital/pkgsettings.svg?branch=master
[travis]: http://travis-ci.org/kpn-digital/pkgsettings?branch=master
[coverage-status-image]: https://img.shields.io/codecov/c/github/kpn-digital/pkgsettings/master.svg
[codecov]: http://codecov.io/github/kpn-digital/pkgsettings?branch=master
[pypi-version]: https://img.shields.io/pypi/v/pkgsettings.svg
[pypi]: https://pypi.python.org/pypi/pkgsettings

