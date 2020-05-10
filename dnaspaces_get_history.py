#
# dnaspaces_get_history.py this script will get client location history from Cisco DNA Spaces and save it into a CSV
# file. The return from the APU /api/location/v1/clients/history is in CSV format.
#
# You need to set your environment variable TOKEN to the token you configure in Cisco DNA Spaces. See README for
# more details.

from os import getpid
from time import strftime
import requests
import os


def get_config():
    if 'TOKEN' in os.environ:
        token = os.environ['TOKEN']
    else:
        print("Please set environment variable TOKEN before running.")
        token = ""
    return token


def get_client_history():
    token = get_config()
    # DNA spaces will return 1 day of history data relevant to time zone.
    url = "https://dnaspaces.io/api/location/v1/history?timeZone=12"
    if len(token) > 0:
        token_str = "Bearer " + token
        headers = {"Authorization": token_str}
        print("Connecting to DNA Spaces. This may take a minute or two.")
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            if response.status_code == 200:
                print("Successfully connected to DNA Spaces. Writing data to file. This will take a while.")
                pid = str(getpid())
                filename = "client-history" + "-" + pid + "-" + strftime("%Y%m%d%H%M") + ".csv"
                lines_read = 0
                with open(filename, "w") as f:
                    for chunk in response.iter_lines(decode_unicode=True):
                        print(chunk, file=f)
                        lines_read += 1
                print(f"Wrote {lines_read:,} lines to file {filename}.")
            else:
                print("Error: unable to connect to DNA Spaces. Got status code", response.status_code)
    print("Finished.")


if __name__ == '__main__':
    get_client_history()
