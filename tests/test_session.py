# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import requests
import responses

from didel.session import Session, ROOT_URL

class TestSession(unittest.TestCase):

    # .get_url

    def test_get_absolute_url(self):
        url = 'http://example.com'
        s = Session()
        self.assertEquals(url, s.get_url(url))

    def test_get_relative_url_root(self):
        url = '/'
        s = Session()
        self.assertEquals('%s/' % ROOT_URL, s.get_url(url))

    def test_get_relative_url(self):
        url = '/foo/bar/qux'
        s = Session()
        self.assertEquals('%s%s' % (ROOT_URL, url), s.get_url(url))


    # .get

    @responses.activate
    def test_get_requests_object(self):
        url = 'http://www.example.com/foo'
        body = "okx&Asq'"
        responses.add(responses.GET, url, body=body, status=200)
        s = Session()
        resp = s.get(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIsInstance(resp, requests.Response)

    @responses.activate
    def test_get_set_default_ua(self):
        url = 'http://www.example.com/foo'
        responses.add(responses.GET, url, body='ok', status=200)
        Session().get(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIn('User-Agent', responses.calls[0].request.headers)

    @responses.activate
    def test_post_requests_object(self):
        url = 'http://www.example.com/foo'
        body = "okx&Asq'"
        responses.add(responses.POST, url, body=body, status=200)
        s = Session()
        resp = s.post(url)
        self.assertEquals(1, len(responses.calls))
        self.assertIsInstance(resp, requests.Response)

    # TODO: login

    @responses.activate
    def test_get_ensure_text_false_on_error(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body='oops', status=404)
        s = Session()
        self.assertFalse(s.get_ensure_text(path, 'oops'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_false_without_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body="that's ok", status=200)
        s = Session()
        self.assertFalse(s.get_ensure_text(path, 'not ok'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_false_without_case_sensitive_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        responses.add(responses.GET, url, body="that's ok", status=200)
        s = Session()
        self.assertFalse(s.get_ensure_text(path, 'OK'))
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_get_ensure_text_true_on_match(self):
        path = '/foo/xyz/aq1'
        url = '%s%s' % (ROOT_URL, path)
        ok = 'okaayy'
        responses.add(responses.GET, url, body="(a%sx" % ok, status=200)
        s = Session()
        self.assertTrue(s.get_ensure_text(path, ok))
        self.assertEquals(1, len(responses.calls))
