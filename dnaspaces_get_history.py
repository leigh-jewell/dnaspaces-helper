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
        print("WARNING: Environment variable TOKEN not set.")
        print(os.environ.keys())
        token = ""
    return token


def write_csv_file(output_text):
    success = False
    pid = str(getpid())
    filename = "client-history" + "-" + pid + "-" + strftime("%Y%m%d%H%M") + ".csv"
    num_records = output_text.text.count("\n")
    with open(filename, "w") as f:
        f.write(output_text)
        f.close()
        print("Wrote {} records to filename {}".format(num_records, filename))


def get_client_history():
    token = get_config()
    if len(token) > 0:
        token_str = "Bearer " + token
        headers = {"Authorization": token_str}
        response = requests.get("https://dnaspaces.io/api/location/v1/clients/history", headers=headers)
        error = False
        if response.status_code == 200:
            print("Successfully retrieved clients from DNA Spaces")
            try:
                data = response.json()
            except ValueError:
                print("Error: unable to decode response as JSON.")
                error = True
        else:
            print("Error: unable to connect to DNA Spaces. Got status code", response.status_code)
            error = True
        if not error:
            print("Writing client data..")
            write_csv_file(response.text)
    print("Finished.")


if __name__ == '__main__':
    get_client_history()
