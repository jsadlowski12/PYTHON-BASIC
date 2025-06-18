"""
Write tests for classes in python_part_2/task_classes.py (Homework, Teacher, Student).
Check if all methods working correctly.
Also check corner-cases, for example if homework number of days is negative.
"""
from unittest import TestCase

from practice.python_part_2.task_classes import Homework, Teacher, Student
from practice.python_part_2.task_read_write_2 import *

class Test_classes(TestCase):
    def setUp(self) -> None:
        self.homework_active = Homework('Learn unittest', 4)
        self.homework_expired = Homework('Expired', 0)
        self.teacher = Teacher('Brown', 'Mark')
        self.student = Student('White', 'Walter')

    def test_homework_is_active(self):
        assert self.homework_active.is_active() == True

    def test_homework_is_not_active(self):
        assert self.homework_expired.is_active() == False
