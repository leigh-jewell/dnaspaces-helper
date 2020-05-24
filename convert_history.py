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


def convert_history(data_file, timezone):
    logging.debug(f"Converting data file {data_file} from timestamp to local timezone.")
    try:
        df = pd.read_csv(data_file)
    except IOError as e:
        logging.error(f"Unable to open csv file to convert. Got error {e}.")
        return False
    return True


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(funcName)s():%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("filename", action="store", required=True,
                        help="Filename of csv to convert timestamp to local timezone")
    parser.add_argument("-tz", "--timezone",
                        dest="timezone", type=int, choices=range(-24, 25),
                        metavar="[-24 to 24]", action='store',
                        help="Time zone offset in hours minutes HH:MM e.g. 10:00 or -4:00")
    args = parser.parse_args()
    convert_history(args.filename, args.timezone)