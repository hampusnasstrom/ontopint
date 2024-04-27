import ontopint
import deepdiff

from common import _load_test_data, _recursive_items

def test_default_keys():
    """test input data with default keys 'value' and 'unit'
    """
    input_jsonld = _load_test_data("test_data_default_keys.jsonld")
    parsed_jsonld = ontopint.parse_units(input_jsonld)
    result = ontopint.export_units(parsed_jsonld)
    assert (len(deepdiff.DeepDiff(input_jsonld, result).keys()) == 0) # no diff

def test_custom_keys():
    """test input data with custom keys 'my_value' and 'my_unit'
    """
    input_jsonld = _load_test_data("test_data_custom_keys.jsonld")
    parsed_jsonld = ontopint.parse_units(input_jsonld)
    result = ontopint.export_units(parsed_jsonld)
    diff = deepdiff.DeepDiff(input_jsonld, result)
    print(deepdiff.DeepDiff(input_jsonld, result))
    assert (len(deepdiff.DeepDiff(input_jsonld, result).keys()) == 0) # no diff

test_custom_keys()