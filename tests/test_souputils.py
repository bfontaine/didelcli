# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import sys, fake_ordereddict, helpers
from bs4 import BeautifulSoup
from didel import souputils
from didel.souputils import parse_homemade_dl

import collections

_collections = collections

def soup(html):
    return BeautifulSoup(html, 'lxml')


class TestSoupUtils(unittest.TestCase):


    # parse_homemade_dl

    def test_parse_homemade_dl_no_defs(self):
        p = BeautifulSoup("<p>simple text.</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([], list(defs.items()))

    def test_parse_homemade_dl_no_defs2(self):
        p = soup("<p>very <i>simple</i> text.</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([], list(defs.items()))

    def test_parse_homemade_dl_def_no_val(self):
        p = soup("<p>yo <b>title:</b></p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([], list(defs.items()))

    def test_parse_homemade_dl_one_def(self):
        p = soup("<p>yo <b>foo</b> bar</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('foo', 'bar')], list(defs.items()))

    def test_parse_homemade_dl_one_def_child_value(self):
        p = soup("<p>yo <b>foo</b> <i>bar</i></p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('foo', 'bar')], list(defs.items()))

    def test_parse_homemade_dl_uppercase_key(self):
        p = soup("<p><b>Yo</b> foo</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('yo', 'foo')], list(defs.items()))

    def test_parse_homemade_dl_uppercase_value(self):
        p = soup("<p><b>yo</b> FOO</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('yo', 'FOO')], list(defs.items()))

    def test_parse_homemade_dl_with_colon(self):
        p = soup("<p><b>yo</b> : FOO</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('yo', 'FOO')], list(defs.items()))

    def test_parse_homemade_dl_with_colon_in_key(self):
        p = soup("<p><b>yo :</b> FOO</p>").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('yo :', 'FOO')], list(defs.items()))

    def test_parse_homemade_dl(self):
        p = soup("""<p><b>a</b> 1<br/>
                <b>b</b> 2 <b>c</b> 3""").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('a', '1'), ('b', '2'), ('c', '3')],
                list(defs.items()))


class TestSoupUtilsPy26(unittest.TestCase):

    def setUp(self):
        sys.modules['collections'] = None
        sys.modules['ordereddict'] = fake_ordereddict
        helpers.reload(souputils)

    def tearDown(self):
        sys.modules['collections'] = collections

    def test_py26_fallback_on_ordereddict(self):
        p = soup("""<p><b>a</b> 1<br/>
                <b>b</b> 2 <b>c</b> 3""").select('p')[0]
        defs = parse_homemade_dl(p)
        self.assertSequenceEqual([('a', '1'), ('b', '2'), ('c', '3')],
                list(defs.items()))
        self.assertEqual(True, getattr(defs, '_fake', False))
