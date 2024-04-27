import os
import ontopint
import json
import pint

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

def test_default_keys():
    """test input data with default keys 'value' and 'unit'
    """
    input_jsonld = _load_test_data("test_data_default_keys.jsonld")
    parsed_jsonld = ontopint.parse_units(input_jsonld)
    del parsed_jsonld["@context"]
    parse_values_count = 0
    for key, value in _recursive_items(parsed_jsonld):
        if key == "value": 
            assert(isinstance(value, pint.Quantity))
            parse_values_count += 1 
        if key == "unit": assert False, "unit key should not be present"
    assert parse_values_count == 2, "result should contain 2 parsed values"

def test_custom_keys():
    """test input data with custom keys 'my_value' and 'my_unit'
    """
    input_jsonld = _load_test_data("test_data_custom_keys.jsonld")
    parsed_jsonld = ontopint.parse_units(input_jsonld)
    del parsed_jsonld["@context"]
    parse_values_count = 0
    for key, value in _recursive_items(parsed_jsonld):
        if key == "my_value": 
            assert(isinstance(value, pint.Quantity))
            parse_values_count += 1 
        if key == "my_unit": assert False, "my_unit key should not be present"
    assert parse_values_count == 2, "result should contain 2 parsed values"
    