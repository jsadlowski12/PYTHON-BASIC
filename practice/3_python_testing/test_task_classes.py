"""
Write tests for classes in python_part_2/task_classes.py (Homework, Teacher, Student).
Check if all methods working correctly.
Also check corner-cases, for example if homework number of days is negative.
"""
from datetime import timedelta
from unittest import TestCase
from practice.python_part_2.task_classes import Homework, Teacher, Student

class TestClasses(TestCase):
    def setUp(self) -> None:
        self.homework_active = Homework('Learn unittest', timedelta(4))
        self.homework_expired = Homework('Expired', timedelta(0))
        self.teacher = Teacher('Brown', 'Mark')
        self.student = Student('White', 'Walter')

    def test_homework_is_active(self):
        assert self.homework_active.is_active() == True

    def test_homework_is_not_active(self):
        assert self.homework_expired.is_active() == False

    def test_teacher_object_creation_and_fields(self):
        assert self.teacher is not None
        assert self.teacher.last_name == 'Brown'
        assert self.teacher.first_name == 'Mark'

    def test_student_object_creation_and_fields(self):
        assert self.student is not None
        assert self.student.last_name == 'White'
        assert self.student.first_name == 'Walter'

    def test_create_homework(self):
        homework = self.teacher.create_homework('Biology', 2)

        assert homework is not None
        assert homework.text == 'Biology'
        assert homework.deadline == timedelta(2)
