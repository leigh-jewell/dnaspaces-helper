from convert_history import change_timezone, timestamp_to_date, convert_history
import pandas as pd
import numpy as np
import logging
import os


def test_change_timezone():
    df = pd.DataFrame({
        'date': ['2020-05-25T0:00']
    }, dtype="datetime64[ns]")
    df['utc'] = df['date'].dt.tz_localize(tz='UTC')
    df['sydney'] = change_timezone(df['utc'], 'Australia/Sydney')
    df['auckland'] = change_timezone(df['utc'], 'Pacific/Auckland')
    assert df.date[0].tzinfo is None
    assert df.utc[0].tzinfo is not None and str(df.utc[0].tzinfo) == "UTC"
    assert (df.utc[0].strftime("%H") == "00")
    assert df.sydney[0].tzinfo is not None and str(df.sydney[0].tzinfo) == "Australia/Sydney"
    assert (df.sydney[0].strftime("%H") == "10")
    assert df.auckland[0].tzinfo is not None and str(df.auckland[0].tzinfo) == "Pacific/Auckland"
    assert (df.auckland[0].strftime("%H") == "12")


def test_timestamp_to_date():
    df = pd.DataFrame({'timestamp': [1590019287571]})
    df['date'] = timestamp_to_date(df['timestamp'])
    assert (df.date[0].strftime("%Y-%m-%d %H:%M.%S") == '2020-05-21 00:01.27')


def test_convert_history():
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        datefmt='%H:%M:%S',
                        filemode="a",
                        level=logging.DEBUG)
    df = pd.DataFrame({"sourcetimestamp": [1590019287571], "firstactiveat": [0], "changedon": [1590019287571]})
    df.to_csv("test_convert_history_tmp.csv")
    new_filename = convert_history("test_convert_history_tmp.csv", "Australia/Sydney", False)
    df_new = pd.read_csv(new_filename)
    assert os.path.isfile(new_filename)
    assert (df_new.sourcetimestamp[0] == '2020-05-21 10:01:27')
    assert (np.isnan(df_new.firstactiveat[0]))
    assert (df_new.changedon[0] == '2020-05-21 10:01:27')
    new_filename = convert_history("test_convert_history_tmp.csv", "Australia/Sydney", True)
    assert os.path.isfile(new_filename)
    assert os.path.isfile(new_filename + ".old")
    try:
        os.remove("./test_convert_history_tmp.csv")
        os.remove(new_filename + ".old")
    except OSError as e:
        logging.error("Unable to delete test files. Got error", e)
