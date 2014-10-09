# -*- coding: UTF-8 -*-

from __future__ import print_function

from getpass import getpass
from sys import argv, exit

from didel import __version__
from didel.config import DidelConfig
from didel.student import Student

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


    def get_student(self):
        username = self.config.get_secret('username')
        passwd = self.config.get_secret('password')
        if username is None or passwd is None:
            print("Configure your login credentials with" \
                  " '%s login:init <username>'" % self.exe)
            return None
        return Student(username, passwd)


    def print_version(self):
        print("DidelCli v%s -- github.com/bfontaine/didelcli" % __version__)


    def print_help(self):
        name_offset = len('action_')
        print("\nUsage:\n\t%s <subcommand> args..." % self.exe)
        print("\nAvailable subcommands:\n")
        for mth in dir(self):
            if not mth.startswith('action_'):
                continue
            cmd = getattr(self, mth)
            doc = cmd.__doc__
            name = mth[name_offset:].replace('_', ':')
            print("%s\n%s" % (name, doc.strip('\n')))


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
        self.config.set(key, value, save=True)


    def action_config_get(self, key):
        """
        Get a configuration variable
        """
        value = self.config.get(key)
        if value is None:
            return 1
        print(value)


    def action_config_list(self):
        """
        Print the actual configuration
        """
        for kv in self.config.items():
            print('%s=%s' % kv)


    def action_login_init(self, username):
        """
        Set your credentials. The command will ask for your password and store
        both your username and password in a secured file. It doesn't check if
        they're valid.
        """
        self.config.set_secret('username', username)
        self.config.set_secret('password', getpass('Password: '))
        self.config.save()


    def action_profile_show(self):
        """
        Show some info about your profile
        """
        s = self.get_student()
        if not s:
            return 1
        print("%s %s (%s)" % (s.firstname, s.lastname, s.username))
        print("Student number: %s" % s.code)
        for key in ('email', 'phone', 'skype'):
            value = getattr(s, key, None)
            if not value:
                continue
            print("%s: %s" % (key.capitalize(), value))


    def action_courses_show(self, code):
        """
        Show some infos about a course
        """
        s = self.get_student()
        if not s:
            return 1
        course = s.get_course(code)
        print("%s (%s)\n" % (course.title, course.teacher))
        print(course.about)


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
    ret = DidelCli(argv).run() or 0
    exit(ret)
