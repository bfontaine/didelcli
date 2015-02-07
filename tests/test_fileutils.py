# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import shutil
from time import sleep
from os import chmod
from os.path import isdir
from tempfile import mkdtemp

from didel.fileutils import date2timestamp, file_mtime, mkdir_p


class TestFileutils(unittest.TestCase):

    def setUp(self):
        self.path = mkdtemp()

        self.first  = self.full_path("foo")
        self.second = self.full_path("bar")

    def tearDown(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def full_path(self, path):
        if path.startswith("/"):
            return path
        return "%s/%s" % (self.path, path)

    def touch(self, path):
        f = open(self.full_path(path), "w")
        f.close()

    # date2timestamp

    def test_date2timestamp_wrong_format_default_0(self):
        self.assertEquals(0, date2timestamp("", 0))
        self.assertEquals(0, date2timestamp("some text", 0))
        self.assertEquals(0, date2timestamp("3.14", 0))

    def test_date2timestamp_good_format_bad_date(self):
        self.assertEquals(0, date2timestamp("31.02.2014", 0))

    def test_date2timestamp_good_format_bad_date_42(self):
        self.assertEquals(42, date2timestamp("31.02.2014", 42))

    def test_date2timestamp_good_date(self):
        d1 = date2timestamp("29.01.2015", 43)
        d2 = date2timestamp("28.02.2015", 42)
        self.assertLess(d1, d2)

    # file_mtime

    def test_mtime_order(self):
        self.touch(self.first)
        sleep(2)
        self.touch(self.second)
        self.assertGreater(file_mtime(self.second), file_mtime(self.first))

    # mkdir_p

    def test_mkdir_p_already_exist(self):
        try:
            mkdir_p(self.path)
        except OSError:
            self.fail("mkdir_p() raised OSError on an existing path")

        self.assertTrue(isdir(self.path))

    def test_mkdir_p_only_leaf_doesnt_exist(self):
        the_dir = self.full_path("foo")
        try:
            mkdir_p(the_dir)
        except OSError:
            self.fail("mkdir_p() raised OSError unexpectedly")

        self.assertTrue(isdir(the_dir))

    def test_mkdir_p_multiple_unexisting_dirs(self):
        the_dir = self.full_path("foo/bar/qux")
        try:
            mkdir_p(the_dir)
        except OSError:
            self.fail("mkdir_p() raised OSError unexpectedly")

        self.assertTrue(isdir(the_dir))

    def test_mkdir_p_should_fail_if_no_permissions(self):
        chmod(self.path, 0)
        self.assertRaises(OSError, lambda: mkdir_p(self.full_path("a")))
