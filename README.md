# Cisco DNA Spaces Helper

A small collection of example Python scripts to easily extract data from [Cisco DNA Spaces](https://dnaspaces.io). 
Initially the scripts will concentrate on location tracking to help with finding where people have travelled.

## Getting Started
* Have a look at the Cisco DNA Spaces API over at [DevNet](https://developer.cisco.com/docs/dna-spaces/#!dna-spaces-location-cloud-api).
To get familar with the APIs available.
* Clone this repository into a directory to get the helper scripts:
```
git clone https://github.com/leigh-jewell/dnaspaces-helper.git
```
### Prerequisites

* Install [Python 3.7+](https://www.python.org/downloads/) with the appropriate distribution for your OS.
* Install [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) using pip which should have been installed with Python3:
```
pip install pipenv
```
Or if you are using [Homebrew](https://brew.sh/) simply run:
```
brew install pipenv
```

* For your script to authenticate with [Cisco DNA Spaces](https://dnaspaces.io) you need to create a token in your account.
Instructions are shown on [DevNet](https://developer.cisco.com/docs/dna-spaces/#!getting-started). Otherwise, simply follow these steps: 
1. Browse to [Detect and Locate](https://dnaspaces.io/locate/) 
2. Click on the menu bar and select "Notifications"
3. Click on "API Keys"
4. Add token 
5. Make a copy of the token string

### Installing

Create the virtual environment using Pipflie.lock. This will ensure the dependencies are installed

```
pipenv install --ignore-pipfile
```

## Running the scrips

The script will use the environment variable 'TOKEN' to authenticate to DNA Spaces. You will need to set this according
to your OS.

OSX:
```
export TOKEN="abcdefghijkl"
```
Windows10:
```
set TOKEN "abcdefghijkl"
```

Use the Pipenv shell to ensure you access the virtual environment created:
```
pipenv shell
```

 You can now run the scripts:

```
python dnaspaces_get_history.py
```
## Options

```
usage: dnaspaces_get_history.py [-h] [-st START_TIME] [-et END_TIME]
                                [-tz TIMEZONE] [-f FILENAME] [-nc]

optional arguments:
  -h, --help            show this help message and exit
  -st START_TIME, --start_time START_TIME
                        Start time in ISO format [YYY-MM-DDThh:mm:ss.s+TZD] If
                        not provided will use -1 day as start time. End time
                        will be start time +1 day if not provided.
  -et END_TIME, --end_time END_TIME
                        End time ISO format [YYY-MM-DDThh:mm:ss.s+TZD]
  -tz TIMEZONE, --timezone TIMEZONE
                        Time zone database name e.g. Australia/Sydney
  -f FILENAME, --filename FILENAME
                        Filename to write the client history data into.
  -nc, --no_convert     Stop the conversion of timestamp to localised date
                        time.
  -ko, --keep_original  Keep the original file with timestamps before conversion.
```

## Examples:

Get the past 1 day of data in the local timezone timestamps to local date and time:

```
python dnaspaces_get_history.py 
```

Get a specific date range in the local timezone. As DNA Spaces can only do 1 day of data at a time. This call
will break time ranges into separate 1 day requests. The date time is in ISO format.

```
python dnaspaces_get_history.py -st=2020-05-25 -et=2020-05-28
```

Get a specific date range in the local timezone and write to file output.csv

```
python dnaspaces_get_history.py -st=2020-05-25 -et=2020-05-28 -f="/tmp/output.csv"
```

Get a specific date range in the local timezone and write to file output.csv but don't convert the timestamps.

```
python dnaspaces_get_history.py -st=2020-05-25 -et=2020-05-28 -nc
```

Get a specific date range in the specified time zone.

```
python dnaspaces_get_history.py -st=2020-05-25 -et=2020-05-28 -tz=Australia/Sydney
```

## Built With

* [Requests](https://requests.readthedocs.io/en/master/) - Requests is an elegant and simple HTTP library for Python, built for human beings.

## Authors

* **Leigh Jewell** - *Initial work* - [Github](https://github.com/leigh-jewell)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to Cisco DNA Spaces for such a great product.
