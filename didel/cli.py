# -*- coding: UTF-8 -*-

from __future__ import print_function

from sys import argv

from didel import __version__
from didel.config import DidelConfig

HELP_FLAGS = ('-h', '-help', '--help')


def get_args(fun):
    """
    Get a list of the arguments of a function
    """
    # http://stackoverflow.com/a/4051447/735926
    try:
        code = fun.func_code
    except AttributeError:  # Python 3
        code = fun.__code__
    return code.co_varnames[:code.co_argcount]


class DidelCli(object):

    def __init__(self, argv):
        self.argv = argv
        self.exe = self.argv.pop(0)
        self.config = DidelConfig.get_default()


    def print_version(self):
        print("DidelCli v%s -- github.com/bfontaine/didelcli" % __version__)


    def print_help(self):
        name_offset = len('action_')
        print("\nUsage:\n\t%s <subcommand> args..." % self.exe)
        print("\nAvailable subcommands:")
        for mth in dir(self):
            if not mth.startswith('action_'):
                continue
            cmd = getattr(self, mth)
            doc = cmd.__doc__
            name = cmd[name_offset:].replace('_', ':')
            print("%10s -- %65s" % (name, doc))


    def print_action_help(self, action, params, docstring=''):
        """
        Print an help text for a subcommand
        """
        params = map(lambda s: '<%s>' % s, params)
        print("Usage:\n\t%s %s %s\n" % (self.exe, action, " ".join(params)))
        if docstring:
            print("%s\n" % docstring.strip())


    def action_config_set(self, key, value):
        """
        Set a configuration variable
        """
        self.config.set(key, value)


    def action_config_get(self, key):
        """
        Get a configuration variable
        """
        print(self.config.get(key))


    def action_config_list(self):
        """
        Print the actual configuration
        """
        for kv in self.config.items():
            print('%s=%s' % kv)


    def run(self):
        """
        Parse the command-line arguments and call the method corresponding to
        the situation.
        """
        # We're using a custom parser here to handle subcommands.
        if len(self.argv) == 0:
            return self.print_help()
        action = self.argv.pop(0)
        if action in HELP_FLAGS:
            self.print_version()
            return self.print_help()
        if action in ('-v', '-version', '--version'):
            return self.print_version()

        # Subcommands are defined as below:
        #   def action_some_keyword(self, ...)
        # defines an action 'some:keyword'. We might need to use classes for
        # subcommands like Thor (Ruby gem), but it'd be too much overhead for
        # now.
        name = 'action_%s' % action.replace(':', '_')
        if not hasattr(self, name):
            print("Unrecognized action '%s'" % action)
            return self.print_help()

        mth = getattr(self, name)
        argv = self.argv
        argc = len(argv)
        params = get_args(mth)[1:]  # remove 'self'

        if argc != len(params) or (argc > 0 and argv[0] in HELP_FLAGS):
            return self.print_action_help(action, params, mth.__doc__)

        return mth(*argv)



def run():
    """
    Start the command-line app
    """
    DidelCli(argv).run()
