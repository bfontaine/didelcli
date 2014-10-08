# -*- coding: UTF-8 -*-
from collections import OrderedDict as _OrderedDict

class OrderedDict(_OrderedDict):

    def __init__(self, *args, **kwargs):
        super(OrderedDict, self).__init__(*args, **kwargs)
        self._fake = True
