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
        self.assertEqual(settings.test_key, 'test_value')

    def test_context_manager(self):
        with settings(test_key='context_manager'):
            self.assertEqual(settings.test_key, 'context_manager')
        self.assertEqual(settings.test_key, 'test_value')

    def test_decorator(self):
        @settings(test_key='decorator')
        def go():
            self.assertEqual(settings.test_key, 'decorator')

        go()
        self.assertEqual(settings.test_key, 'test_value')

    def test_decorator_in_class(self):
        unittest_self = self

        class Dummy(object):
            @settings(test_key='decorator_in_class')
            def go(self):
                unittest_self.assertEqual(settings.test_key,
                                          'decorator_in_class')

        Dummy().go()
        self.assertEqual(settings.test_key, 'test_value')


if __name__ == '__main__':
    import sys

    sys.exit(unittest.main())
