# Cisco DNA Spaces Helper

A small collection of example Python scripts to easily extract data from Cisco DNA Spaces. Initially the scripts will
concentrate on location tracking to help with finding where people have travelled.

## Getting Started
Clone this repository into a directory:
```
git clone https://github.com/leigh-jewell/dnaspaces-helper.git
```

### Prerequisites

* Install [Python 3.7+](https://www.python.org/downloads/) with the appropriate distribution for your OS.
* Install [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) using pip which should have been installed with Python 3.7+
```
pip install pipenv
```
* [Cisco DNA Spaces](https://dnaspaces.io) To authenticate with DNA Spaces you need to create a token. 
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

The script will use the environment variable 'TOKEN' to authenticate to DNA Spaces. You will need to set this accordin
to your OS.

OSX:
```
export TOKEN="abcdefghijkl"
```
Windows10:
```
set TOKEN "abcdefghijkl"
```

 You can now run the scripts:

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
