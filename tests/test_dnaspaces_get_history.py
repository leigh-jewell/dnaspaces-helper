from dnaspaces_get_history import get_arguments, get_config, check_file_writable, get_filename
import datetime as datetime
import pytz
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR


def test_get_arguments():
    args = get_arguments(["-st=2020-05-21T10:00",
                          "-et=2020-05-21T11:00",
                          "-tz=Australia/Sydney",
                          "-f=a_filename",
                          "-ct=True"])
    assert args.start_time
    assert datetime.datetime(args.start_time.year, args.start_time.month, args.start_time.day)
    assert args.end_time
    assert datetime.datetime(args.end_time.year, args.end_time.month, args.end_time.day)
    assert args.timezone
    assert args.timezone in pytz.all_timezones
    assert args.filename
    assert args.convert_time
    assert args.convert_time is True


def test_get_config():
    assert get_config() == ""
    os.environ["TOKEN"] = "TEST_TOKEN"
    assert get_config() == "TEST_TOKEN"


def test_check_file_writable():
    test_file = "test_file"
    f = open(test_file, "w")
    f.write("")
    f.close()
    assert check_file_writable(test_file)
    os.chmod(test_file, S_IREAD | S_IRGRP | S_IROTH)
    assert check_file_writable(test_file) is False
    os.chmod(test_file, S_IWUSR | S_IREAD)
    os.remove(test_file)


def test_get_filename():
    assert type(get_filename()) is str
    assert len(get_filename()) > 0
    assert get_filename("test") == "test"
