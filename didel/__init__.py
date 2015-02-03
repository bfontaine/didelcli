# -*- coding: UTF-8 -*-

"""
This module provides a set of functions and classes to interface with DidEL.
"""

__version__ = '0.1.1'

# Shortcuts
from didel.courses import Course, CourseAssignment, CourseAssignments
from didel.session import Session
from didel.student import Student

# silent Pyflakes
Course, CourseAssignment, CourseAssignments, Session, Student
