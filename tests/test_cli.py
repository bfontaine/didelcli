# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from didel.cli import DidelCli

class TestCli(unittest.TestCase):

    def test_init_with_exe_as_first_arg(self):
        c = DidelCli(["foo"])
        self.assertEquals("foo", c.exe)
