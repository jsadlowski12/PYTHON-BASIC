"""
Create 3 classes with interconnection between them (Student, Teacher,
Homework)
Use datetime module for working with date/time
1. Homework takes 2 attributes for __init__: tasks text and number of days to complete
Attributes:
    text - task text
    deadline - datetime.timedelta object with date until task should be completed
    created - datetime.datetime object when the task was created
Methods:
    is_active - check if task already closed
2. Student
Attributes:
    last_name
    first_name
Methods:
    do_homework - request Homework object and returns it,
    if Homework is expired, prints 'You are late' and returns None
3. Teacher
Attributes:
     last_name
     first_name
Methods:
    create_homework - request task text and number of days to complete, returns Homework object
    Note that this method doesn't need object itself
PEP8 comply strictly.
"""
from datetime import datetime, timedelta


class Teacher:
    def __init__(self, last_name: str, first_name: str):
        self.last_name = last_name
        self.first_name = first_name

    def create_homework(self, text: str, days_to_complete: int):
        return Homework(text, days_to_complete)


class Student:
    def __init__(self, last_name: str, first_name: str):
        self.last_name = last_name
        self.first_name = first_name

    def do_homework(self, homework: 'Homework'):
        if homework.is_active():
            return homework
        else:
            print("You are late.")
            return None

class Homework:
    def __init__(self, text: str, days_to_complete: int):
        self.text = text
        self.created = datetime.now()
        self.deadline = self.created + timedelta(days=days_to_complete)

    def is_active(self):
        closed = False

        if datetime.now() >= self.deadline:
            print("Task closed.")
            closed = True
        else:
            print("Task in progress.")

        return closed


if __name__ == '__main__':
    teacher = Teacher('Dmitry', 'Orlyakov')
    student = Student('Vladislav', 'Popov')
    print("Teacher: ", teacher.last_name)
    print("Student: ", student.last_name)  # Petrov

    expired_homework = teacher.create_homework('Learn functions', 0)
    print("Expired homework creation date: ", expired_homework.created)  # Example: 2019-05-26 16:44:30.688762
    print("Expired homework deadline: ", expired_homework.deadline)  # 0:00:00
    print("Expired homework text: ", expired_homework.text)  # 'Learn functions'

    # create function from method and use it
    create_homework_too = teacher.create_homework
    oop_homework = create_homework_too('create 2 simple classes', 5)
    print("oop homework deadline: ", oop_homework.deadline)  # 5 days, 0:00:00

    student.do_homework(oop_homework)
    student.do_homework(expired_homework)  # You are late
