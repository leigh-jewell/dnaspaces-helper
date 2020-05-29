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
python dnaspaces_get_history.py
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
