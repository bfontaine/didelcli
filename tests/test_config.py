# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from didel.config import DidelConfig

class TestDidelConfig(unittest.TestCase):

    def setUp(self):
        DidelConfig._default = None
