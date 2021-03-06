import pytest
from datetime import datetime, timedelta, timezone
from get_date_range import valid_time, split_dates, add_timezone, convert_timestamp_millisecond, get_date_range
from tzlocal import get_localzone
import pytz
from constants import MAX_DAYS, HOURLY_TIME_CHUNK_SIZE
import time


def test_valid_time():
    no_timezone = datetime.now()
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=5)
    more_than_30days = start + timedelta(days=MAX_DAYS + 1)
    start_future = datetime.now(timezone.utc) + timedelta(days=2)
    end_future = datetime.now(timezone.utc) + timedelta(days=1)
    assert not valid_time(no_timezone, no_timezone)
    assert not valid_time(more_than_30days, more_than_30days)
    assert not valid_time(start, more_than_30days)
    assert not valid_time(start_future, end_future)
    assert valid_time(start, end)
    with pytest.raises(Exception):
        valid_time("Invalid", "Invalid")


def test_split_dates():
    end = datetime.now(timezone.utc)
    one_day = end - timedelta(days=1)
    assert len(split_dates(one_day, end)) == 24/HOURLY_TIME_CHUNK_SIZE
    start = end - timedelta(days=10)
    assert len(split_dates(start, end)) == 10*(24/HOURLY_TIME_CHUNK_SIZE)
    assert split_dates(start, end)[0] == (start, start + timedelta(hours=HOURLY_TIME_CHUNK_SIZE))
    assert split_dates(start, end)[-1] == (start + timedelta(days=9, hours=24-HOURLY_TIME_CHUNK_SIZE), end)


def test_add_timezone():
    no_time_zone = datetime.now()
    with_time_zone = add_timezone(no_time_zone)
    assert with_time_zone.tzinfo is not None
    assert str(with_time_zone.tzinfo) in pytz.all_timezones


def test_convert_timestamp_millisecond():
    now = datetime.now()
    assert convert_timestamp_millisecond(now) == round(now.timestamp()*1000)
    assert convert_timestamp_millisecond(datetime(1969, 1, 1)) < 0


def test_get_date_range():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=1)
    end_str = end.strftime("%Y-%m-%d")
    start_str = start.strftime("%Y-%m-%d")
    current_time = time.localtime()
    if current_time.tm_isdst:
        # Daylight savings in effect
        start1 = datetime.fromisoformat(start_str + "T10:00+11:00")
        end1 = datetime.fromisoformat(end_str + "T10:00+11:00")
        dates1 = get_date_range(start1, end1)
        start2 = datetime.fromisoformat(start_str + "T11:00")
        end2 = datetime.fromisoformat(end_str + "T10:00")
    else:
        start1 = datetime.fromisoformat(start_str + "T10:00+10:00")
        end1 = datetime.fromisoformat(end_str + "T10:00+10:00")
        dates1 = get_date_range(start1, end1)
        start2 = datetime.fromisoformat(start_str + "T10:00")
        end2 = datetime.fromisoformat(end_str + "T10:00")
    dates2 = get_date_range(start2, end2)
    dates3 = get_date_range(start2, end2, "Australia/Sydney")
    assert len(dates1) == 24/HOURLY_TIME_CHUNK_SIZE
    assert dates1[0] == (start1, start1 + timedelta(hours=HOURLY_TIME_CHUNK_SIZE))
    assert str(dates1[0][0].utcoffset()) == str(start1.utcoffset())
    assert str(dates1[0][1].utcoffset()) == str(start1.utcoffset())
    assert str(dates2[0][0].tzinfo) in pytz.all_timezones
    assert str(dates2[0][0].tzinfo) == str(get_localzone())
    assert str(dates2[0][1].tzinfo) == str(get_localzone())
    assert str(dates3[0][0].tzinfo) == "Australia/Sydney"
    assert str(dates3[0][1].tzinfo) == "Australia/Sydney"
    with pytest.raises(Exception):
        get_date_range(start2, end2, "Invalid Timezone")
