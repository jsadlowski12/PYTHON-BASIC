import pytest
import importlib

res = importlib.import_module('practice.1_python_part_1.task4')

def test_calculate_power_with_difference():
    result = res.calculate_power_with_difference([1, 2, 3])
    assert result == [1, 4, 7]