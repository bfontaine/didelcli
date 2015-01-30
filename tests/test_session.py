# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import requests
import responses

from didel.session import Session, URLS, ROOT_URL

class TestSession(unittest.TestCase):

    def test_ua_set_on_init(self):
        ua = 'th+is/an user 4gent'
        s = Session(user_agent=ua)
        self.assertEquals(ua, s.user_agent)

    def test_set_headers_defaults_user_agent_already_present(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {'headers': {'User-Agent': ua}}
        s = Session(user_agent='another/user_agent v1')
        s._set_header_defaults(kwargs)  # in-place change
        self.assertEquals(ua, kwargs['headers']['User-Agent'])

    def test_set_headers_defaults_user_agent_not_present_no_headers(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {}
        s = Session(user_agent=ua)
        s._set_header_defaults(kwargs)  # in-place change
        self.assertIn('headers', kwargs)
        self.assertEquals(ua, kwargs['headers']['User-Agent'])

    def test_set_headers_defaults_user_agent_not_present_with_headers(self):
        ua = 'some/random - user+agent v42.1.3.21'
        kwargs = {'headers': {'X-Foo': '42'}}
        s = Session(user_agent=ua)
        s._set_header_defaults(kwargs)  # in-place change
        self.assertIn('headers', kwargs)
        self.assertEquals(ua, kwargs['headers']['User-Agent'])


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
    def test_logout_false_on_error(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body='nope', status=500)
        s = Session()
        self.assertFalse(s.logout())
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_logout_false_without_match(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body='nothing here', status=200)
        s = Session()
        self.assertFalse(s.logout())
        self.assertEquals(1, len(responses.calls))

    @responses.activate
    def test_logout_true_on_success(self):
        url = URLS['logout']
        responses.add(responses.GET, url, body="""
            Logout successful :) """, status=200)
        s = Session()
        self.assertTrue(s.logout())
        self.assertEquals(1, len(responses.calls))

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
