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

from argparse import ArgumentParser
import logging
import pandas as pd
import numpy as np
from pytz import all_timezones
from tzlocal import get_localzone


def change_timezone(col, timezone):
    return col.dt.tz_convert(tz=timezone)


def timestamp_to_date(col):
    return pd.to_datetime(col, origin='unix', unit='ms', utc=True, errors="coerce")


def convert_history(data_file, timezone):
    logging.debug(f"Converting data file {data_file} from timestamp to local timezone.")
    date_cols = ["sourcetimestamp", "firstactiveat", "changedon"]
    try:
        df = pd.read_csv(data_file)
    except IOError as e:
        logging.error(f"Unable to open csv file to convert. Got error {e}.")
        return False
    # Some timestamps are zero and need to replace with Nan to avoid getting set to 1/1/1970
    df[date_cols] = df[date_cols].replace({0: np.nan})
    df.update(df[date_cols].apply(pd.to_datetime, origin='unix', unit='ms', utc=True, errors="coerce"))
    df.update(df[date_cols].apply(change_timezone, args=(timezone,)))
    new_filename = data_file.replace(".csv", "-converted.csv")
    try:
        df.to_csv(new_filename, date_format='%Y-%m-%d %H:%M:%S.%f'[:-3])
        logging.info(f"Converted file written to {new_filename}.")
    except IOError as e:
        logging.error(f"Unable to write csv file {new_filename}. Got error {e}.")
        return False
    return True


def get_local_tz():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo


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
    args = parser.parse_args()
    if args.timezone is None:
        tz = get_localzone()
        logging.debug(f"Using local timezone {tz}")
    elif args.timezone not in all_timezones:
        tz = get_localzone()
        logging.error(f"Timezone {args.timezone} is not valid. Using local timezone {tz}")
    else:
        tz = args.timezone
    convert_history(args.filename, tz)
