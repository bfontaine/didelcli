# -*- coding: UTF-8 -*-

from __future__ import print_function

import inspect
from getpass import getpass
from os.path import expanduser
from sys import argv, exit

from didel import __version__
from didel.config import DidelConfig
from didel.student import Student
from didel.exceptions import DidelLoginRequired, DidelServerError

HELP_FLAGS = ('-h', '-help', '--help')


class DidelCli(object):

    def __init__(self, argv):
        self.argv = argv
        self.exe = self.argv.pop(0)
        self.config = DidelConfig.get_default()

    def get_student(self, fetchInfos=False):
        username, passwd = self.config.get_credentials()
        if username is None or passwd is None:
            print("Configure your login credentials with" \
                  " '%s login:init <username>'" % self.exe)
            return None
        return Student(username, passwd, autofetch=fetchInfos)


    def get_course(self, code, student=None):
        """
        Shortcut for ``self.get_student().get_course(code)``
        """
        if student is None:
            student = self.get_student()
        if not student:
            return None
        code = self.config.get('alias.%s' % code, code)
        return student.get_course(code)


    def print_version(self):
        print("DidelCli v%s -- http://git.io/didelcli" % __version__)


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
        print("Usage:\n\t%s %s %s\n" % (self.exe, action, params))
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
            return False
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
        s = self.get_student(fetchInfos=True)
        if not s:
            return False
        print("%s %s (%s)\n" % (s.firstname, s.lastname, s.username))
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
        course = self.get_course(code)
        if not course:
            return False
        print("%s (%s)\n" % (course.title, course.teacher))
        print(course.about)


    def action_courses_enroll(self, code, key=None):
        """
        Enroll in a course.
        """
        course = self.get_course(code)
        if not course:
            return False
        return course.enroll(key=key)


    def action_courses_unenroll(self, code):
        """
        Unenroll from a course.
        """
        course = self.get_course(code)
        if not course:
            return False
        return course.unenroll()


    def action_courses_open(self, code):
        """
        Open a course's page in a browser
        """
        course = self.get_course(code)
        if not course:
            return False
        import webbrowser
        webbrowser.open(course.url())


    def action_courses_alias(self, alias, code):
        """
        Add an alias for a course
        """
        self.config.set('alias.%s' % alias, code, save=True)


    def action_assignments_list(self, course_code):
        """
        List a course's assignments
        """
        course = self.get_course(course_code)
        for i in range(len(course.assignments)):
            # 'for ag in course.assignments' isn't supported for now
            asg = course.assignments[i]
            idx = i + 1  # start indexes at 1
            print("%d) %s (%s)" % (idx, asg.title, asg.end))


    def action_assignments_show(self, course_code, index):
        """
        Show a course's assignment. The index can be obtained with
        'assignments:list', the first assignment is '1', the second '2', etc.
        """
        index = int(index)
        course = self.get_course(course_code)
        if not course:
            return False
        a = course.assignments[index - 1]  # indexes start at 1
        print(a.title)
        print("%s -> %s" % (a.begin, a.end))
        print("Type: %s" % a.submission_type)
        print("Visibility: %s" % a.visibility)
        print("Work Type: %s" % a.work_type)


    def action_assignments_submit(self, course_code, index, title, filename):
        """
        Submit an assigment. 'title' is its title (e.g. "TP 1"), and 'filename'
        is the file that should be attached to it.
        """
        index = int(index)
        s = self.get_student()
        if not s:
            return False
        course = self.get_course(course_code, s)
        a = course.assignments[index - 1]  # indexes start at 1
        with open(expanduser(filename), 'rb') as f:
            return a.submit(s, title, f)


    def action_pull(self):
        """
        Pull all documents from each followed course in a folder, using the
        path defined with ``didel pull:save``.
        """
        student = self.get_student() # check if student is initialized in `SOURCE_FILE`
        path = self.config.get("Courses.path")
        if path is None:
            print("Configure your path to pull with" \
                  " '%s pull:save <path>'" % self.exe)
            return None
        print("pull to %s" % path)
        for course in student.get_all_courses():
            course.synchronize_docs(path)


    def action_pull_save(self, path):
        """
        Define the path where we'll download all files with ``didel pull``.
        """
        self.config.set("Courses.path", path, True)
        self.action_pull()


    def run(self):
        """
        Parse the command-line arguments and call the method corresponding to
        the situation.
        """
        # We're using a custom parser here to handle subcommands.
        argv = self.argv
        argc = len(argv)
        if argc == 0:
            return self.print_help()
        action = argv.pop(0)
        argc -= 1
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

        fun = getattr(self, name)

        # dynamically check if enough arguments were given on the command line
        spec = inspect.getargspec(fun)
        # skip 'self'
        spec_args = (spec.args or ())[1:]
        spec_defaults = (spec.defaults or ())[1:]
        defaults_len = len(spec_defaults)
        required_len = len(spec_args) - defaults_len

        if argc < required_len or (argc > 0 and argv[0] in HELP_FLAGS):
            defaults = list(reversed(spec_args))[:defaults_len]
            args = []
            for arg in spec_args:
                fmt = '<%s>'
                if arg in defaults:
                    fmt = '[%s]' % fmt
                args.append(fmt % arg)

            if spec.varargs:
                args.append('[<%s...>]' % spec.varargs)

            print("Usage:\n\t%s %s %s" % (self.exe, action, ' '.join(args)))
            return False

        return fun(*argv)


def abort(msg, code=1):
    """
    Print a message and exit.
    """
    print(msg)
    exit(code)


def run():
    """
    Start the command-line app
    """
    try:
        ret = DidelCli(argv).run()
    except KeyboardInterrupt:
        abort("Bye!", 0)
    except DidelLoginRequired:
        abort("Error: Login required.")
    except DidelServerError as e:
        abort("%s" % e)

    exit(1) if ret is None or ret == False else exit(0)
