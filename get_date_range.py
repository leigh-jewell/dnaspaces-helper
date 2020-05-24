from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import logging
import pytz
from tzlocal import get_localzone


def valid_time(start, end):
    max_historical_time = datetime.now(timezone.utc) - timedelta(days=30)
    min_time = datetime.now(timezone.utc)
    valid = True
    if start < max_historical_time:
        logging.error("Start time cannot be more than 30 days in the past.")
        valid = False
    if start > end + timedelta(days=30):
        logging.error("End time cannot be greater than 30 days after start time.")
        valid = False
    if end > min_time:
        logging.error("End time cannot be in the future.")
        valid = False
    if start > end:
        logging.error("Start time cannot be before end time")
        valid = False
    return valid


def split_dates(start=None, end=None):
    # Create a list of tuples (start_time, end_time) that are each 1 day apart + end time
    if start is None:
        start = datetime.now(timezone.utc)
    if end is None:
        end = start + timedelta(days=1)
    time_range_list = []
    if valid_time(start, end):
        one_day = timedelta(days=1)
        time_range_list = []
        while start + one_day < end:
            time_range_list.append((start, start + one_day))
            start += one_day
        time_range_list.append((start, end))
    logging.debug(f"Split time range into {len(time_range_list)} days")
    return time_range_list


def add_timezone(time_no_tz, tz):
    if time_no_tz.tzinfo is not None:
        logging.debug("Timezone has been provided in ISO string")
        time_tz = args.start_time
    else:
        logging.debug(f"No timezone in time {time_no_tz} provided")
        if tz is None:
            local_tz = pytz.timezone(get_localzone())
            time_tz = time_no_tz.astimezone(local_tz)
            logging.debug(f"Adding system timezone {time_tz.tzinfo} to time {time_no_tz}")
        elif tz not in pytz.all_timezones:
            logging.error(f"Timezone {tz} provided is not in time zone list. Using local")
            local_tz = pytz.timezone(get_localzone())
            time_tz = time_no_tz.astimezone(local_tz)
            logging.debug(f"Adding system timezone {time_tz.tzinfo} to time {time_no_tz}")
        else:
            time_tz = time_no_tz.astimezone(pytz.timezone(tz))
            logging.debug(f"Using timezone parameter {time_tz.tzinfo} for time {time_no_tz}")
    print(type(time_tz))
    return time_tz


def convert_timestamp_millisecond(time_convert):
    ms_real = time_convert.timestamp()*1000
    ms_int = round(ms_real)
    return str(ms_int)


def get_date_range(start, end, local_tz):
    # Assumes that start_time, end_time are datetime formatted
    start_time_tz = add_timezone(start, local_tz)
    end_time_tz = add_timezone(end, local_tz)
    return split_dates(start_time_tz, end_time_tz)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("start_time", type=datetime.fromisoformat,
                        help="Start time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]")
    parser.add_argument("end_time", type=datetime.fromisoformat,
                        help="End time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]")
    parser.add_argument("-tz", "--timezone", dest="timezone", type=str, choices=pytz.all_timezones,
                        help="Time zone name as per https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
    args = parser.parse_args()
    time_range = get_date_range(args.start_time, args.end_time, args.timezone)
    for (start_time, end_time) in time_range:
        print("Local",
              start_time.strftime("%Y-%m-%d %H:%M"),
              end_time.strftime("%Y-%m-%d %H:%M"))
        print("UTC",
              start_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
              end_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"))
        print("Timestamp (msec)",
              convert_timestamp_millisecond(start_time),
              convert_timestamp_millisecond(end_time))
