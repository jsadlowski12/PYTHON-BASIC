"""
Write tests for division() function in python_part_2/task_exceptions.py
In case (1,1) it should check if exception were raised
In case (1,0) it should check if return value is None and "Division by 0" printed
If other cases it should check if division is correct

TIP: to test output of print() function use capfd fixture
https://stackoverflow.com/a/20507769
"""
import pytest

from practice.python_part_2.task_exceptions import division, DivisionByOneException

def test_division_ok(capfd):
    result = division(2, 2)
    out, err = capfd.readouterr()
    assert out == "1\nDivision finished\n"
    assert result == 1


def test_division_by_zero(capfd):
    result = division(1, 0)
    out, err = capfd.readouterr()
    assert out == "Division by 0\nDivision finished\n"
    assert result is None


def test_division_by_one(capfd):
    with pytest.raises(DivisionByOneException) as e:
        division(1, 1)
        out, err = capfd.readouterr()
        assert out == "Division finished\n"
    assert "Deletion on 1 get the same result" in str(e.value)

