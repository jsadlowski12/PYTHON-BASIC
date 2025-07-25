"""
Write tests for a read_numbers function.
It should check successful and failed cases
for example:
Test if user inputs: 1, 2, 3, 4
Test if user inputs: 1, 2, Text

Tip: for passing custom values to the input() function
Use unittest.mock patch function
https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch

TIP: for testing builtin input() function create another function which return input() and mock returned value
"""
import io
from unittest.mock import patch
from practice.python_part_2.task_input_output import read_numbers

class TestCompareInputAndOutput():

    @patch('sys.stdin', io.StringIO("\n".join(["1", "2", "3", "4"])))
    def test_read_numbers_without_text_input(self):
        result = read_numbers(4)
        expected_result = 'Avg: 2.5'
        assert result == expected_result

    @patch('sys.stdin', io.StringIO("\n".join(["1", "2", "Test"])))
    def test_read_numbers_with_text_input(self):
        result = read_numbers(3)
        expected_result = 'Avg: 1.5'
        assert result == expected_result
