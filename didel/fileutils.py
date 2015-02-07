# -*- coding: UTF-8 -*-

from os import stat, makedirs
from os.path import isdir
from time import mktime
from datetime import datetime
import errno

def date2timestamp(text, default=None):
    """
    Return a timestamp from a date text, assuming it was formatted as it is on
    the documents page of a course on Didel. Note that it assumes you're in the
    same timezone as DidEL (which is hosted in France).
    """
    try:
        date = datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        return default
    return mktime(date.timetuple())


def file_mtime(path):
    """
    Return the last modification time of a file
    """
    return stat(path).st_mtime


def mkdir_p(path):
    """
    Equivalent of ``mkdir -p`` in Python
    """
    # adapted from http://stackoverflow.com/a/600612/735926
    try:
        makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and isdir(path):
            return
        raise
