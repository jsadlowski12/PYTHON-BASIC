from task_1 import calculate_days, WrongFormatException
import pytest
from freezegun import freeze_time


def test_calculate_days_wrong_format():
    with pytest.raises(WrongFormatException, match="Wrong format of the date."):
        result = calculate_days('10-07-2021')
        assert result is None

@freeze_time("2021-10-06")
def test_calculate_days_past():
    result = calculate_days('2021-10-05')
    assert result == 1

@freeze_time("2021-10-06")
def test_calculate_days_future():
    result = calculate_days('2021-10-07')
    assert result == -1