#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pkgsettings
----------------------------------

Tests for `pkgsettings` module.
"""

import unittest

from pkgsettings import Settings

settings = Settings()
settings.configure(test_key='test_value')


class TestPkgsettings(unittest.TestCase):
    def setUp(self):
        super(TestPkgsettings, self).setUp()

    def test_default_settings(self):
        self.assertEqual('test_value', settings.test_key)

    def test_context_manager(self):
        with settings(test_key='context_manager'):
            self.assertEqual('context_manager', settings.test_key)
        self.assertEqual('test_value', settings.test_key)

    def test_decorator(self):
        @settings(test_key='decorator')
        def go():
            self.assertEqual('decorator', settings.test_key)

        go()
        self.assertEqual('test_value', settings.test_key)

    def test_decorator_in_class(self):
        _self = self

        class Dummy(object):
            @settings(test_key='decorator_in_class')
            def go(self):
                _self.assertEqual('decorator_in_class', settings.test_key)

        Dummy().go()
        self.assertEqual('test_value', settings.test_key)

    def test_as_dict(self):
        with settings(test=True):
            expected = dict(test=True, test_key='test_value')
            self.assertEqual(expected, settings.as_dict())


if __name__ == '__main__':
    import sys

    sys.exit(unittest.main())
