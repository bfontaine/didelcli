# -*- coding: UTF-8 -*-

from __future__ import print_function

from sys import argv

from didel import __version__

class DidelCli(object):

    def __init__(self, argv):
        self.argv = argv
        self.exe = self.argv.pop(0)


    def print_version(self):
        print("DidelCli v%s -- github.com/bfontaine/didelcli" % __version__)


    def print_help(self):
        name_offset = len('action_')
        self.print_version()
        print("\nUsage:\n\tdidel <subcommand> args...")
        print("\nAvailable subcommands:")
        for mth in dir(self):
            if not mth.startswith('action_'):
                continue
            cmd = getattr(self, mth)
            doc = cmd.__doc__
            name = cmd[name_offset:].replace('_', ':')
            print("%10s -- %65s" % (name, doc))


    def run(self):
        if len(self.argv) == 0:
            return self.print_help()
        action = self.argv.pop(0)
        if action in ('-h', '-help', '--help'):
            return self.print_help()
        if action in ('-v', '-version', '--version'):
            return self.print_version()

        name = 'action_%s' % action.replace(':', '_')
        if not hasattr(self, name):
            print("Unrecognized action '%s'" % action)
            return self.print_help()

        return getattr(self, name)(self.argv)



def run():
    """
    Start the command-line app
    """
    DidelCli(argv).run()
