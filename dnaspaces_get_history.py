#
# dnaspaces_get_history.py this script will get client location history from Cisco DNA Spaces and save it into a CSV
# file. The return from the APU /api/location/v1/clients/history is in CSV format.
#
# You need to set your environment variable TOKEN to the token you configure in Cisco DNA Spaces. See README for
# more details.
from argparse import ArgumentParser
from datetime import datetime
import requests
import logging
from os import path, access, W_OK, environ
from get_date_range import get_date_range
from convert_history import convert_history
from get_date_range import convert_timestamp_millisecond
import pytz


def get_arguments(passed_in=None):
    parser = ArgumentParser()
    parser.add_argument("-st", "--start_time", dest="start_time", type=datetime.fromisoformat,
                        help="Start time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]"
                               "For example:"
                               "Just date 2020-05-01"
                               "Just date and time 2020-05-01 local timezone of OS used or with -tz option"
                               "Including timezone 2020-05-01 10:00:00+10:00"
                               "End time will be start time +1 day if not provided.")
    parser.add_argument("-et", "--end_time", dest="end_time", type=datetime.fromisoformat,
                        help="End time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]")
    parser.add_argument("-tz", "--timezone", dest="timezone", type=str, choices=pytz.all_timezones,
                        help="Time zone name as per https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
    parser.add_argument("-f", "--filename", dest="filename", type=str,
                        help="Filename to write the client history data into.")
    parser.add_argument("-ct", "--convert_time", dest="convert_time", type=bool, default=False,
                        help="Convert timestamp columns to local date time according to timezone parameter.")
    args = parser.parse_args(passed_in)
    logging.debug("Got arguments", args)
    return args


def get_config():
    if 'TOKEN' in environ:
        token = environ['TOKEN']
    else:
        logging.error("Please set environment variable TOKEN before running.")
        token = ""
    return token


def check_file_writable(full_file_name):
    if path.exists(full_file_name):
        # path exists
        if path.isfile(full_file_name):
            return access(full_file_name, W_OK)
        else:
            return False
    parent_dir = path.dirname(full_file_name)
    if not parent_dir:
        parent_dir = '.'
    # target is creatable if parent dir is writable
    return access(parent_dir, W_OK)


def get_client_history(time_tuples_list, write_file):
    token = get_config()
    # DNA spaces will return 1 day of history data.
    url = "https://dnaspaces.io/api/location/v1/history"
    if check_file_writable(write_file):
        logging.debug(f"File {write_file} is suitable for writing")
        valid_file = True
    else:
        logging.error(f"File {write_file} cannot be written. Check path and permissions")
        valid_file = False
    if len(token) > 0 and valid_file:
        token_str = "Bearer " + token
        headers = {"Authorization": token_str}
        logging.info("Connecting to DNA Spaces. This may take a minute or two.")
        lines_read = 0
        with open(filename, "w") as f:
            for (start, end) in time_tuples_list:
                payload = {"startTime": convert_timestamp_millisecond(start),
                           "endTime": convert_timestamp_millisecond(end)}
                logging.debug(f"Using URL params {payload}")
                with requests.get(url, params=payload, headers=headers, stream=True) as response:
                    if response.status_code == 200:
                        logging.info("Connected to DNA Spaces. Writing data to file. This will take a while.")
                        for chunk in response.iter_lines(decode_unicode=True):
                            print(chunk, file=f)
                            lines_read += 1
                        logging.info(f"Wrote {lines_read:,} lines to file {write_file}.")
                    else:
                        logging.error("Error: unable to connect to DNA Spaces. Got status code", response.status_code)
                        break
    logging.info("Finished.")
    return filename


def get_filename(fn=None):
    if fn is None:
        generated_fn = "client-history" + "-" + datetime.now().strftime("%Y%m%d%H%M") + ".csv"
        logging.debug(f"No filename provided, generated filename {generated_fn}.")
        return generated_fn
    else:
        return fn


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        filename="get_history.log",
                        datefmt='%Y-%m-%d %H:%M.%S',
                        filemode="a",
                        level=logging.DEBUG)
    cmd_args = get_arguments()
    time_split = get_date_range(cmd_args.start_time, cmd_args.end_time, cmd_args.timezone)
    filename = get_filename(cmd_args.filename)
    get_client_history(time_split, filename)
    if cmd_args.convert_time:
        logging.debug(f"Converting filename {filename} timestamps to local time with timezone f{args.timezone}.")
        convert_history(filename, args.timezone)
