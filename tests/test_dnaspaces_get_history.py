from dnaspaces_get_history import get_arguments, get_config, check_file_writable, get_filename, \
    get_client_history, valid_date, main
import pytz
import os
from datetime import datetime, timedelta, timezone
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import httpretty
from constants import URL
import pandas as pd


def test_get_client_history(tmpdir):
    tmpdir = str(tmpdir)
    test_filename = os.path.join(tmpdir, 'temp.csv')
    httpretty.enable()  # enable HTTPretty so that it will monkey patch the socket module
    httpretty.register_uri(
        httpretty.GET,
        URL,
        body='tenantid,macaddress,devicetype,campusid,buildingid,floorid,floorhierarchy,coordinatex,coordinatey,'
             'sourcetimestamp,maxdetectedapmac,maxdetectedband,detectingcontrollers,firstactiveat,'
             'locatedsinceactivecount,changedon,manufacturer,associated,maxdetectedrssi,ssid,username,'
             'associatedapmac,associatedaprssi,maxdetectedslot,ipaddress\n'
             '16655,9c:ff:d0:aa:50:ff,CLIENT,b4537bffe15045978d758ed1812670f5,7147effa7e389c41abc7a20dbaa2c6824,'
             'c6e3594a4e24a3feeddeadbeef9e1b28287,System Campus,13.3026,42.9256,1589086604182,'
             '9c:ee:d0:aa:50:ee,IEEE_802_11_B,172.20.0.1,1589072492071,88,1589086604182,Rivet Networks,true,'
             '-52,Test-WiFI,test_user,00:aa:ff:a5:e1:dd,-52,0,"10.10.10.10, fe80:0000:0000:0000:9c:ee:d0:aa:50:ee"',
        status=200,
        content_type="text/csv",
    )
    end = datetime.now()
    start = end - timedelta(days=1)
    assert get_client_history([], "") == 0
    assert get_client_history([("invalid date", "invalid date")], "") == 0
    assert get_client_history([(start, end)], "") == 0
    assert get_client_history([(start, end)], test_filename) == 0
    os.environ["TOKEN"] = "TEST_TOKEN"
    assert get_client_history([(start, end)], test_filename) == 2
    df = pd.read_csv(test_filename)
    assert df.shape == (1, 25)
    assert df.loc[0][0] == 16655
    assert df.loc[0][-1] == "10.10.10.10, fe80:0000:0000:0000:9c:ee:d0:aa:50:ee"
    httpretty.disable()
    httpretty.reset()
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET,
        URL,
        status=400,
    )
    assert get_client_history([(start, end)], test_filename) == 0
    httpretty.disable()
    httpretty.reset()


def test_main(tmpdir):
    tmpdir = str(tmpdir)
    test_filename = os.path.join(tmpdir, 'temp.csv')
    httpretty.enable()  # enable HTTPretty so that it will monkey patch the socket module
    httpretty.register_uri(
        httpretty.GET,
        URL,
        body='tenantid,macaddress,devicetype,campusid,buildingid,floorid,floorhierarchy,coordinatex,coordinatey,'
             'sourcetimestamp,maxdetectedapmac,maxdetectedband,detectingcontrollers,firstactiveat,'
             'locatedsinceactivecount,changedon,manufacturer,associated,maxdetectedrssi,ssid,username,'
             'associatedapmac,associatedaprssi,maxdetectedslot,ipaddress\n'
             '16655,9c:ff:d0:aa:50:ff,CLIENT,b4537bffe15045978d758ed1812670f5,7147effa7e389c41abc7a20dbaa2c6824,'
             'c6e3594a4e24a3feeddeadbeef9e1b28287,System Campus,13.3026,42.9256,1589086604182,'
             '9c:ee:d0:aa:50:ee,IEEE_802_11_B,172.20.0.1,1589072492071,88,1589086604182,Rivet Networks,true,'
             '-52,Test-WiFI,test_user,00:aa:ff:a5:e1:dd,-52,0,"10.10.10.10, fe80:0000:0000:0000:9c:ee:d0:aa:50:ee"',
        status=200,
        content_type="text/csv",
    )
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=1)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    os.environ["TOKEN"] = "DUMMY"
    del os.environ["TOKEN"]
    assert main(["-st", start_str, "-et", end_str, "-f", test_filename]) is False
    os.environ["TOKEN"] = "TEST_TOKEN"
    assert main(["-st", start_str, "-et", end_str, "-f", test_filename])
    del os.environ["TOKEN"]
    httpretty.disable()
    httpretty.reset()


def test_get_arguments():
    args = get_arguments(["-st=2020-05-21T10:00",
                          "-et=2020-05-21T11:00",
                          "-tz=Australia/Sydney",
                          "-f=a_filename"])
    assert args.start_time
    assert datetime(args.start_time.year, args.start_time.month, args.start_time.day)
    assert args.end_time
    assert datetime(args.end_time.year, args.end_time.month, args.end_time.day)
    assert args.timezone
    assert args.timezone in pytz.all_timezones
    assert args.filename
    assert args.convert_time
    args = get_arguments(["-st=2020-05-21T10:00",
                          "-et=2020-05-21T11:00",
                          "-tz=Australia/Sydney",
                          "-f=a_filename",
                          "-nc"])
    assert args.convert_time is False


def test_get_config():
    assert get_config() == ""
    os.environ["TOKEN"] = "TEST_TOKEN"
    assert get_config() == "TEST_TOKEN"
    del os.environ["TOKEN"]


def test_check_file_writable(tmpdir):
    tmpdir = str(tmpdir)
    test_file = os.path.join(tmpdir, 'test_file')
    f = open(test_file, "w")
    f.write("")
    f.close()
    assert check_file_writable(test_file)
    os.chmod(test_file, S_IREAD | S_IRGRP | S_IROTH)
    assert check_file_writable(test_file) is False
    os.chmod(test_file, S_IWUSR | S_IREAD)


def test_get_filename():
    assert type(get_filename()) is str
    assert len(get_filename()) > 0
    assert get_filename("test") == "test"


def test_valid_date():
    assert valid_date(datetime.now())
    assert valid_date("not date") is False

