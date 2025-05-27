import pytest
from main import convert_datetime
from datetime import datetime


@pytest.fixture
def test_datetime():
    date_time_str = "20250319 040401"
    date_time = convert_datetime(date_time=date_time_str)
    return date_time


def test_success_convert_datetime(test_datetime):
    assert test_datetime == datetime(2025, 3, 19, 4, 4, 1)
