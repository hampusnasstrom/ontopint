import json
import os


def _load_test_data(file_name: str) -> dict:
    """loads a json file from the test data folder

    Parameters
    ----------
    file_name
        the name of the json file

    Returns
    -------
        the content of the file as dict
    """
    data = {}
    with open(os.path.join(os.path.dirname(__file__), "data", file_name)) as f:
        data = json.load(f)
    return data

def _recursive_items(dictionary: dict):
    """Returns a generator of tuples for every key-value pair in the dict

    Parameters
    ----------
    dictionary
        any (nested) dict

    Yields
    ------
        iterator for key-value tuples of the dict
    """
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from _recursive_items(value)
        else:
            yield (key, value)