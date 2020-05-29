from datetime import datetime, timedelta, timezone
from get_date_range import valid_time, split_dates, add_timezone, convert_timestamp_millisecond, get_date_range
import pytz


def test_valid_time():
    no_timezone = datetime(2020, 5, 1, 1, 0, 0)
    start = datetime(2020, 5, 1, 1, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(days=5)
    more_than_30days = start + timedelta(days=31)
    start_future = datetime.now(timezone.utc) + timedelta(days=2)
    end_future = datetime.now(timezone.utc) + timedelta(days=1)
    assert not valid_time(no_timezone, no_timezone)
    assert not valid_time(more_than_30days, more_than_30days)
    assert not valid_time(start, more_than_30days)
    assert not valid_time(start_future, end_future)
    assert valid_time(start, end)


def test_split_dates():
    start = datetime(2020, 5, 1, 1, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(days=10)
    assert len(split_dates(start, end)) == 10
    assert split_dates(start, end)[0] == (start, start + timedelta(days=1))
    assert split_dates(start, end)[-1] == (start + timedelta(days=9), end)


def test_add_timezone():
    no_time_zone = datetime(2020, 5, 1, 1, 0, 0)

    assert add_timezone(no_time_zone).tzinfo is not None


def test_convert_timestamp_millisecond():
    assert False


def test_get_date_range():
    assert False
