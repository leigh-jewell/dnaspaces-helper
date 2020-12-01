#
# dnaspaces_get_history.py this script will get client location history from Cisco DNA Spaces and save it into a CSV
# file. The return from the APU /api/location/v1/clients/history is in CSV format.
#
# You need to set your environment variable TOKEN to the token you configure in Cisco DNA Spaces. See README for
# more details.
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import requests
import logging
from os import path, access, W_OK, environ
from get_date_range import get_date_range
from convert_history import convert_history
from get_date_range import convert_timestamp_millisecond
from constants import URL, MAX_REQUEST_RETRIES, REQUEST_TIMEOUT
from tzlocal import get_localzone
from time import sleep


def get_arguments(passed_in=None):
    parser = ArgumentParser()
    parser.add_argument("-st", "--start_time", dest="start_time",
                        type=datetime.fromisoformat,
                        help="Start time in ISO format [YYY-MM-DDThh:mm:ss.s+TZD] "
                               "If not provided will use -1 day as start time. "
                               "End time will be start time +1 day if not provided.")
    parser.add_argument("-et", "--end_time", dest="end_time",
                        type=datetime.fromisoformat,
                        help="End time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]")
    parser.add_argument("-tz", "--timezone", dest="timezone", type=str, default=str(get_localzone()),
                        help="Time zone database name e.g. Australia/Sydney")
    parser.add_argument("-f", "--filename", dest="filename", type=str,
                        help="Filename to write the client history data into.")
    parser.add_argument("-nc", "--no_convert", dest="convert_time", default=True, action='store_false',
                        help="Stop the conversion of timestamp to localised date time.")
    parser.add_argument("-ko", "--keep_original", dest="keep_original", default=False, action='store_true',
                        help="Keep the original file with timestamps as .old")
    args = parser.parse_args(passed_in)
    if args.start_time is not None:
        logging.debug("Got arguments " + args.start_time.strftime("%Y-%m-%d %H:%M"))
    if args.end_time is not None:
        logging.debug("Got arguments " + args.end_time.strftime("%Y-%m-%d %H:%M"))
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


def valid_date(date):
    try:
        datetime(date.year, date.month, date.day)
        return True
    except TypeError:
        return False
    except AttributeError:
        return False


def get_api_response(payload, headers):
    attempts = 0
    current_timeout = REQUEST_TIMEOUT
    while attempts < MAX_REQUEST_RETRIES:
        try:
            response = requests.get(URL, params=payload, headers=headers, stream=True, timeout=current_timeout)
            if response.status_code == requests.codes.ok:
                break
            else:
                logging.error(f"{attempts}.Error with REST to DNA Spaces got {response.status_code} "
                              f"should have got {requests.codes.ok}. Service may be too busy.")
                logging.error(f"This is attempt {attempts} of maximum {MAX_REQUEST_RETRIES}. Retrying..")
                attempts += 1
        except requests.ConnectionError as e:
            logging.error(f"Got a network connection error {e}. Please check {URL} is reachable.")
            attempts += 1
        except requests.Timeout as e:
            logging.error(f"Got a timeout with request {e}. Incrementing timeout {current_timeout}")
            current_timeout += 60
            attempts += 1
        except requests.exceptions.RequestException as e:
            logging.error(f"Got an unknown exception from requests {e}. Exiting.")
            raise SystemExit(e)
        sleep(5)

    return response


def get_client_history(time_tuples_list, write_file):
    token = get_config()
    lines_read = 0
    # DNA spaces will return 1 day of history data.
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
        printed_header = False
        with open(write_file, "w") as f:
            for (start, end) in time_tuples_list:
                if valid_date(start) and valid_date(end):
                    logging.info(f"Using date range {start} to {end}")
                    payload = {"startTime": convert_timestamp_millisecond(start),
                               "endTime": convert_timestamp_millisecond(end)}
                    logging.debug(f"Using URL params {payload}")
                    response = get_api_response(payload, headers)
                    if response.status_code == requests.codes.ok:
                        logging.info("Connected to DNA Spaces. Writing data to file. This will take a while.")
                        new_request = True
                        chunk_line_count = 0
                        try:
                            for chunk in response.iter_lines(decode_unicode=True):
                                if chunk_line_count > 0:
                                    print(chunk, file=f)
                                elif not printed_header and new_request:
                                    print(chunk, file=f)
                                    printed_header = True
                                chunk_line_count += 1
                                lines_read += 1
                        except requests.exceptions.Timeout as e:
                            logging.error(f"Connection timed out. Not all data was received. {e}")
                        except requests.exceptions.RequestException as e:
                            logging.error(f"Got an exception with the connection. Not all data was received. {e}")
                        logging.info(f"Wrote {lines_read:,} lines to file {write_file}.")
                    else:
                        logging.error(f"Unable to connect to {URL}. Got status code {response.status_code}" +
                                      f"Message {response.text}")
                        break
                else:
                    logging.error(f"Invalid start and/or end dates.")
    return lines_read


def get_filename(fn=None):
    if fn is None:
        generated_fn = "client-history" + "-" + datetime.now().strftime("%Y%m%d%H%M") + ".csv"
        logging.debug(f"No filename provided, generated filename {generated_fn}.")
        return generated_fn
    else:
        return fn


def main(passed_args=None):
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        filename="get_history.log",
                        datefmt='%Y-%m-%d %H:%M.%S',
                        filemode="a",
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    cmd_args = get_arguments(passed_args)
    time_split = get_date_range(cmd_args.start_time, cmd_args.end_time, cmd_args.timezone)
    filename = get_filename(cmd_args.filename)
    lines = get_client_history(time_split, filename)
    if lines > 0 and cmd_args.convert_time:
        logging.debug(f"Converting filename {filename} timestamps to local time with timezone {cmd_args.timezone}.")
        convert_history(filename, cmd_args.timezone, cmd_args.keep_original)
    logging.info("Finished.")
    return lines > 0


if __name__ == '__main__':
    main()
