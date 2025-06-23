from task_2 import math_calculate, OperationNotFoundException
import pytest

def test_math_calculate_ceil():
    result = math_calculate('ceil', 10.7)
    assert result == 11

def test_math_calculate_log():
    result = math_calculate('log', 1024, 2)
    assert result == 10.0

def test_math_calculate_exception():
    with pytest.raises(OperationNotFoundException):
        result = math_calculate('notexist')
        assert result is None