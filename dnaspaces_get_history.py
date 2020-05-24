#
# dnaspaces_get_history.py this script will get client location history from Cisco DNA Spaces and save it into a CSV
# file. The return from the APU /api/location/v1/clients/history is in CSV format.
#
# You need to set your environment variable TOKEN to the token you configure in Cisco DNA Spaces. See README for
# more details.

from os import getpid
from time import strftime
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import requests
import os
import logging


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


def date_range(start=None, end=None):
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


def add_arguments():
    a_parser = ArgumentParser()
    a_parser.add_argument("-st", "--start_time", dest="start_time", type=datetime.fromisoformat,
                          help="Start time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]"
                               "For example:"
                               "Just date 2020-05-01"
                               "Just date and time 2020-05-01 local timezone of OS used or with -tz option"
                               "Including timezone 2020-05-01 10:00:00+10:00"
                               "End time will be start time +1 day if not provided.")
    a_parser.add_argument("-et", "--end_time", dest="end_time", type=datetime.fromisoformat,
                          help="End time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]")
    a_parser.add_argument("-tz", "--timezone", dest="timezone", type=int, choices=range(-24, 25), metavar="[-24 to 24]",
                          help="Time zone offset in hours minutes HH:MM e.g. 10:00 or -4:00")
    return a_parser


def add_timezone(time_no_tz, tz):
    if time_no_tz.tzinfo is not None:
        logging.debug("Timezone has been provided in ISO string")
        time_tz = args.start_time
    else:
        logging.debug("No timezone in time provided")
        if tz is None:
            logging.debug("Using system timezone")
            time_tz = time_no_tz.astimezone()
        else:
            logging.debug("Using timezone parameter for timezone")
            time_tz = time_no_tz.replace(tzinfo=timezone(timedelta(hours=tz)))
    return time_tz


def get_time_filters(test_args):
    parser = add_arguments()
    if test_args:
        args = parser.parse_args(test_args)
    else:
        args = parser.parse_args()
    logging.debug(args)
    start_time_tz = add_timezone(args.start_time, args.timezone)
    end_time_tz = add_timezone(args.end_time, args.timezone)
    return start_time_tz, end_time_tz


def convert_timestamp_millisecond(time_convert):
    ms_real = time_convert.timestamp()*1000
    ms_int = round(ms_real)
    return str(ms_int)


def get_config():
    if 'TOKEN' in os.environ:
        token = os.environ['TOKEN']
    else:
        logging.error("Please set environment variable TOKEN before running.")
        token = ""
    return token


def get_client_history(time_tuples_list):
    token = get_config()
    # DNA spaces will return 1 day of history data.
    url = "https://dnaspaces.io/api/location/v1/history"
    if len(token) > 0:
        token_str = "Bearer " + token
        headers = {"Authorization": token_str}
        logging.info("Connecting to DNA Spaces. This may take a minute or two.")
        pid = str(getpid())
        filename = "client-history" + "-" + pid + "-" + strftime("%Y%m%d%H%M") + ".csv"
        logging.debug(f"Using filename {filename}")
        lines_read = 0
        with open(filename, "w") as f:
            for (start, end) in time_tuples_list:
                logging.debug(f"Using filter start {start} end {end}")
                logging.debug(f"Using filter utc start {start_time.astimezone(timezone.utc)} end {end_time.astimezone(timezone.utc)}")
                payload = {"startTime": convert_timestamp_millisecond(start),
                           "endTime": convert_timestamp_millisecond(end)}
                logging.debug(f"Using URL params {payload}")
                with requests.get(url, params=payload, headers=headers, stream=True) as response:
                    if response.status_code == 200:
                        logging.info("Connected to DNA Spaces. Writing data to file. This will take a while.")
                        for chunk in response.iter_lines(decode_unicode=True):
                            print(chunk, file=f)
                            lines_read += 1
                        logging.info(f"Wrote {lines_read:,} lines to file {filename}.")
                    else:
                        logging.error("Error: unable to connect to DNA Spaces. Got status code", response.status_code)
                        break
    logging.info("Finished.")


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        filename="get_history.log",
                        datefmt='%H:%M:%S',
                        filemode="a",
                        level=logging.DEBUG)
    start_time, end_time = get_time_filters(['-st', '2020-05-21 10:00', '-et', '2020-05-21 11:00', '-tz', '10'])
    time_range = date_range(start_time, end_time)
    get_client_history(time_range)
