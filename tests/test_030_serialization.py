import ontopint
import deepdiff

def test_default_keys():
    """test input data with default keys 'value' and 'unit'
    """

    test = {
        "value": ontopint.ureg.Quantity(
            1.123, ontopint.ureg.from_ucum("eV")
        )
    }
    expected = {
        "value": 1.123,
        "unit": "qunit:EV"
    }
    result = ontopint.export_units(test)
    del result["@context"]
    assert (len(deepdiff.DeepDiff(expected, result).keys()) == 0) # no diff

def test_custom_keys():
    """test input data with custom keys 'my_value' and 'my_unit'
    """
    test = {
        "@context": {
            "qudt": "http://qudt.org/schema/qudt/",
            "qunit": "http://qudt.org/vocab/unit/",
            "qkind": "http://qudt.org/vocab/quantkind/",
            "my_unit": {
                "@id": "qudt:hasUnit",
                "@type": "@id"
            },
            "my_value": "qudt:value",
        },
        "my_value": ontopint.ureg.Quantity(
            1.123, ontopint.ureg.from_ucum("eV")
        )
    }
    expected = {
        "my_value": 1.123,
        "my_unit": "qunit:EV"
    }
    result = ontopint.export_units(test)
    del result["@context"]
    assert (len(deepdiff.DeepDiff(expected, result).keys()) == 0) # no diff

    