# -*- coding: UTF-8 -*-

import platform

# builtin (before 3.0) function 'reload(<module>)'
# from https://github.com/bfontaine/term2048/blob/3e36f1b0/tests/helpers.py#L26
if platform.python_version() < '3.0':
    reload = reload
else:
    import imp
    reload = imp.reload
