import ontopint
import pint

from common import _load_test_data, _recursive_items

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
    