from datetime import date, timedelta
from typing import Iterator


class DateRangeUtilException(Exception):
    pass


def date_range(start: date, end: date) -> Iterator[date]:
    """Returns list of dates between start and end.

    end date is included in returned list.
    """
    if start > end:
        raise DateRangeUtilException(f"start date: '{start}' can not greater than end date: {end}")
    for i in range((end - start).days + 1):
        yield start + timedelta(days=i)
