from datetime import date

import pytest

from src.data_scrappers.utils import date_range, DateRangeUtilException


def test_date_range_returns_proper_number_of_days():
    # given
    start = date(2022, 1, 1)
    end = date(2023, 4, 21)

    # when
    dates = list(date_range(start, end))

    # then
    assert len(dates) == 476


@pytest.mark.parametrize(
    "start, end, expected",
    [
        # February - regular year
        (date(2022, 2, 27), date(2022, 3, 1), [date(2022, 2, 27), date(2022, 2, 28), date(2022, 3, 1)]),
        # February - leap year
        (date(2020, 2, 28), date(2020, 3, 1), [date(2020, 2, 28), date(2020, 2, 29), date(2020, 3, 1)]),
        # Break year
        (date(2021, 12, 31), date(2022, 1, 1), [date(2021, 12, 31), date(2022, 1, 1)]),
    ],
)
def test_date_range_returns_proper_dates(start, end, expected):
    # when
    dates = list(date_range(start, end))

    # then
    assert dates == expected


def test_date_range_throws_error_when_start_is_later_than_end():
    # given
    start = date(2023, 1, 1)
    end = date(2022, 4, 21)

    # then
    with pytest.raises(DateRangeUtilException):
        next(date_range(start, end))


def test_date_range_returns_proper_day_when_start_end_are_equal():
    # given
    start = date(2022, 3, 15)
    end = date(2022, 3, 15)

    # when
    dates = list(date_range(start, end))

    # then
    assert dates == [date(2022, 3, 15)]
