# -*- coding: UTF-8 -*-

try:
    from collections import OrderedDict
except ImportError:  # Python 2.6
    from ordereddict import OrderedDict

import re
from bs4 import NavigableString

START_COLON = re.compile(r'^\s*:\s*')

def parse_homemade_dl(el):
    """
    Parse an homemade ``dl`` element. Those are text elements such as
    ``small`` or ``p`` with labels in bold (``b``) and values in normal font
    weight. For example: ::

        <small><b>Title</b> : foo<br/>
        <b>From</b> 2014/02/13 <b>to</b> 2014/03/25</small>

    This parses each ``b`` element as a ``dict`` key and the text following it
    as its value.
    Result: ::

        {'title': 'foo',
         'from': '2014/02/13',
         'to': '2014/03/25'}
    """
    attrs = OrderedDict()
    key = None

    for child in el.children:
        if child.name == 'b':
            key = child.get_text().strip().lower()
            continue
        if key:
            # avoid <br/>s and empty texts
            if not isinstance(child, NavigableString):
                child = child.get_text()
            t = child.strip()
            if t:
                attrs[key] = re.sub(START_COLON, '', t)
                key = None

    return attrs
