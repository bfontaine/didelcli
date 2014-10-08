# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from didel import __version__

class TestMisc(unittest.TestCase):

    def test_version_format(self):
        self.assertRegexpMatches(__version__, r'^\d+\.\d+\.\d+')
