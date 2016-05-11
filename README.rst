pkgsettings
===========

.. image:: https://secure.travis-ci.org/kpn-digital/py-pkgsettings.svg?branch=master
    :target:  http://travis-ci.org/kpn-digital/py-pkgsettings?branch=master

.. image:: https://img.shields.io/codecov/c/github/kpn-digital/py-pkgsettings/master.svg
    :target: http://codecov.io/github/kpn-digital/py-pkgsettings?branch=master

.. image:: https://img.shields.io/pypi/v/pkgsettings.svg
    :target: https://pypi.python.org/pypi/pkgsettings

.. image:: https://readthedocs.org/projects/py-pkgsettings/badge/?version=latest
    :target: http://py-pkgsettings.readthedocs.org/en/latest/?badge=latest


Goal
----

The goal of this package is to offer an easy, generic and extendable way
of configuring a package.

Installation
------------
.. start_installation

.. code-block:: bash

    $ pip install pkgsettings

.. end_installation

Usage
-----
.. start_usage
.. code-block:: python

    from pkgsettings import Settings

    # Create the settings object for your package to use
    settings = Settings()

    # Now lets defined the default settings
    settings.configure(hello='World', debug=False)

By calling the configure you actually inject a ``layer`` of settings.
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

It is also possible to pass an object instead of kwargs.
The settings object will call ``getattr(ur_object, key)``
An example below:

.. code-block:: python

    class MySettings(object):
        def __init__(self):
            self.debug = True

    settings = Settings()
    settings.configure(MySettings())
    print(settings.debug) # This will print: True

More advanced usage
-------------------

The settings object can also be used as context manager:

.. code-block:: python

    with settings(debug=True):
        print(settings.debug) # This will print: True

    print(settings.debug) # This will print: False

Additionally you can also use this as a decorator:

.. code-block:: python

    @settings(debug=True)
    def go()
        print(settings.debug) # This will print: True

    go()

    print(settings.debug) # This will print: False


.. end_usage
