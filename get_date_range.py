from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import logging
import pytz
from tzlocal import get_localzone
from constants import MAX_DAYS, HOURLY_TIME_CHUNK_SIZE


def valid_time(start, end):
    max_historical_time = datetime.now(timezone.utc) - timedelta(days=MAX_DAYS)
    min_time = datetime.now(timezone.utc)
    valid = True
    try:
        datetime(year=start.year, month=start.month, day=start.day, hour=start.hour, minute=start.minute)
    except ValueError:
        logging.error("Invalid start date.")
        valid = False
    except AttributeError:
        logging.error("Invalid attributes for start date.")
        valid = False
    try:
        datetime(year=end.year, month=end.month, day=end.day, hour=end.hour, minute=end.minute)
    except ValueError:
        logging.error("Invalid enddate.")
        valid = False
    except AttributeError:
        logging.error("Invalid attributes for end date.")
        valid = False
    if start.tzinfo is None:
        logging.error("Start time has no timezone. Can't compare")
        valid = False
    elif end.tzinfo is None:
        logging.error("End time has no timezone. Can't compare")
        valid = False
    elif start < max_historical_time:
        logging.error("Start time cannot be more than 30 days in the past.")
        valid = False
    elif start > end + timedelta(days=30):
        logging.error("End time cannot be greater than 30 days after start time.")
        valid = False
    elif end > min_time:
        logging.error("End time cannot be in the future.")
        valid = False
    elif start > end:
        logging.error("Start time cannot be before end time")
        valid = False
    return valid


def split_dates(start=None, end=None):
    # Create a list of tuples (start_time, end_time) that are each chunked CHUNK_SIZE apart + end time
    time_range_list = []
    if valid_time(start, end):
        time_chunk = timedelta(hours=HOURLY_TIME_CHUNK_SIZE)
        time_range_list = []
        while start + time_chunk < end:
            time_range_list.append((start, start + time_chunk))
            start += time_chunk
            logging.debug(f"Append {start} to {start + time_chunk} to time range")
        time_range_list.append((start, end))
        logging.debug(f"Append {start} to {end} to time range")
    logging.debug(f"Split time range into {len(time_range_list)} time chunks.")
    return time_range_list


def add_timezone(time_no_tz, tz=None):
    if time_no_tz.tzinfo in pytz.all_timezones:
        logging.debug("Valid timezone has been provided in ISO string")
        time_tz = time_no_tz
    else:
        logging.debug(f"No timezone in time {time_no_tz} exists.")
        if tz is None:
            local_tz = get_localzone()
            time_tz = time_no_tz.astimezone(local_tz)
            logging.debug(f"Adding system timezone {time_tz.tzinfo} to time {time_no_tz}")
        else:
            try:
                time_tz = time_no_tz.astimezone(pytz.timezone(tz))
                logging.debug(f"Using timezone parameter {time_tz.tzinfo} for time {time_no_tz}")
            except ValueError:
                logging.error(f"Timezone {tz} not a valid time zone.")
                raise ValueError("Not a valid timezone.")

    return time_tz


def check_dates_exist(start, end):
    if end is None:
        end = datetime.now(timezone.utc)
        logging.debug(f"No end date, using today {end}")
    if start is None:
        start = end - timedelta(days=1)
        logging.debug(f"No start date, using today - 1 day {start}")
    return start, end


def convert_timestamp_millisecond(time_convert):
    ms_real = time_convert.timestamp()*1000
    ms_int = round(ms_real)
    return ms_int


def get_date_range(start, end, local_tz=None):
    # Assumes that start_time, end_time are datetime formatted
    (start, end) = check_dates_exist(start, end)
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
    parser.add_argument("-tz", "--timezone", dest="timezone", type=str,
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
