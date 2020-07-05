# Records in the history file
# tenantid, macaddress, \
# devicetype, \
# campusid, \
# buildingid, \
# floorid, \
# floorhierarchy, \
# coordinatex, \
# coordinatey, \
# sourcetimestamp, \
# maxdetectedapmac, \
# maxdetectedband, \
# detectingcontrollers, \
# firstactiveat, \
# locatedsinceactivecount, \
# changedon, \
# manufacturer, \
# associated, \
# maxdetectedrssi, \
# ssid, \
# username, \
# associatedapmac, \
# associatedaprssi, \
# maxdetectedslot, \
# ipaddress

history_dict = {
    'tenantid': 'category',
    'macaddress': 'str',
    'devicetype': 'category',
    'campusid': 'category',
    'buildingid': 'category',
    'floorid': 'category',
    'floorhierarchy': 'str',
    'coordinatex': 'str',
    'coordinatey': 'str',
    'sourcetimestamp': 'str',
    'maxdetectedapmac': 'str',
    'maxdetectedband': 'category',
    'detectingcontrollers': 'category',
    'firstactiveat': 'str',
    'locatedsinceactivecount': 'str',
    'changedon': 'str',
    'manufacturer': 'str',
    'associated': 'str',
    'maxdetectedrssi': 'str',
    'ssid': 'category',
    'username': 'str',
    'associatedapmac': 'str',
    'associatedaprssi': 'str',
    'maxdetectedslot': 'str',
    'ipaddress': 'str',
    'staticdevice': 'str',
    'recordtype': 'str',
    'computetype': 'str',
    'source': 'str',
    'machashed': 'str',
}

from argparse import ArgumentParser
import logging
import pandas as pd
import numpy as np
from pytz import all_timezones
from tzlocal import get_localzone
import os


def change_timezone(col, timezone):
    # Must have tz set otherwise will fail
    try:
        convert_col = col.dt.tz_convert(tz=timezone)
    except AttributeError as e:
        logging.error(f"The column is not a date time type or there is no time zone from which to convert. Error {e}")
        convert_col = col
    return convert_col


def timestamp_to_date(col):
    return pd.to_datetime(col, origin='unix', unit='ms', utc=True, errors="coerce")


def convert_history(data_file, timezone, keep_original):
    logging.debug(f"Converting data file {data_file} from timestamp to local timezone.")
    date_cols = ["sourcetimestamp", "firstactiveat", "changedon"]
    chunk_size = 10 ** 5
    first_chuck = True
    total_chunks = 0
    try:
        tmp_data_file = data_file + ".old"
        os.rename(data_file, tmp_data_file)
        try:
            for df in pd.read_csv(tmp_data_file, chunksize=chunk_size):
                # Some timestamps are zero and need to replace with Nan to avoid getting set to 1/1/1970
                df[date_cols] = df[date_cols].replace(to_replace=0, value=np.nan)
                df.update(df[date_cols].apply(pd.to_datetime, origin='unix', unit='ms', utc=True, errors="coerce"))
                df.update(df[date_cols].apply(change_timezone, args=(timezone,)))
                try:
                    df.to_csv(data_file, date_format='%Y-%m-%d %H:%M:%S.%f'[:-3], mode='a', header=first_chuck)
                    first_chuck = False
                    total_chunks += chunk_size
                    logging.info(f"Converted file chunk {total_chunks:,} written to {data_file}.")
                except IOError as e:
                    logging.error(f"Unable to write csv file {data_file}. Got error {e}.")
                    return None
        except IOError as e:
            logging.error(f"Unable to open csv file to convert. Got error {e}.")
            return None
    except IOError as e:
        logging.error(f"Tried to rename old file {data_file}.old but failed with error {e}")
    if not keep_original:
        try:
            os.remove(tmp_data_file)
        except IOError as e:
            logging.error(f"Tried to delete old file {data_file}.old but failed with error {e}")
    return data_file


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("filename", action="store",
                        help="Filename of csv to convert timestamp to local timezone")
    parser.add_argument("-tz", "--timezone",
                        dest="timezone",
                        help="Time zone offset in hours minutes HH:MM e.g. 10:00 or -4:00")
    parser.add_argument("-ko", "--keep_original", dest="keep_original", default=False, action='store_true',
                        help="Keep the original file with timestamps as .old")
    args = parser.parse_args()
    if args.timezone is None:
        tz = get_localzone()
        logging.debug(f"Using local timezone {tz}")
    elif args.timezone not in all_timezones:
        tz = get_localzone()
        logging.error(f"Timezone {args.timezone} is not valid. Using local timezone {tz}")
    else:
        tz = args.timezone
    convert_history(args.filename, tz, args.keep_original)
