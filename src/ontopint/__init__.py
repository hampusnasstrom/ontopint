import json

import rdflib
from pyld import jsonld

# from pint import UnitRegistry
from ucumvert import PintUcumRegistry

# ureg = UnitRegistry()
ureg = PintUcumRegistry()

processing_context = {
    'qudt': 'http://qudt.org/schema/qudt/',
    'qunit': 'http://qudt.org/vocab/unit/',
    'qkind': 'http://qudt.org/vocab/quantkind/',
    'unit': {'@id': 'qudt:hasUnit', '@type': '@id'},
    'quantity': {'@id': 'qudt:hasQuantityKind', '@type': '@id'},
    'value': 'qudt:value',
}

def get_ucum_code_from_unit_iri(unit_iri):
    graph = rdflib.Graph()
    graph.parse(unit_iri)
    result = graph.query(
        f'SELECT * WHERE {{<{unit_iri}> <http://qudt.org/schema/qudt/ucumCode> ?ucumCode}}'
    )
    ucum_code = str(result.bindings[0]['ucumCode'])
    return ucum_code 
class UnitDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'unit' in obj and 'value' in obj:
            return ureg.Quantity(obj['value'], obj['unit'])
        unit = None
        unit_defs = [
            v for k, v in obj.items() if isinstance(v, str) and v.startswith('qudt:')
        ]
        if len(unit_defs) > 1:
            raise ValueError('More that one unit definition')
        if unit_defs:
            iri = unit_defs[0].replace('qudt:', 'http://qudt.org/vocab/unit/')
            graph = rdflib.Graph()
            graph.parse(iri)
            result = graph.query(
                f'SELECT * WHERE {{<{iri}> <http://qudt.org/schema/qudt/symbol> ?symbol}}'
            )
            unit = result.bindings[0]['symbol']
            for k, v in obj.items():
                if isinstance(v, float):
                    obj[k] = ureg.Quantity(v, unit)
        return obj


def _replace_units(obj, context, original_key_lookup_dict):
    if isinstance(obj, dict):
        expanded_obj = jsonld.expand({**obj, "@context": context}, context)
        compacted_obj = jsonld.compact(expanded_obj, processing_context)
        if 'unit' in compacted_obj and 'value' in compacted_obj:
            # note: "urn:ontopint:iri" is just any iri not existing in the input data
            unit_iri = jsonld.expand(
                    {"@context": {**context, "urn:ontopint:iri": {"@type": "@id"}}, "urn:ontopint:iri": compacted_obj["unit"]}, {}
                )[0]["urn:ontopint:iri"][0]["@id"]
            obj.pop(original_key_lookup_dict['unit'])
            ucum_code = get_ucum_code_from_unit_iri(unit_iri)
            obj[original_key_lookup_dict['value']] = ureg.Quantity(
                obj[original_key_lookup_dict['value']], ureg.from_ucum(ucum_code)
            )
        for key, value in obj.items():
            obj[key] = _replace_units(value, context, original_key_lookup_dict)
        return obj
    elif isinstance(obj, list):
        return [
            _replace_units(value, context, original_key_lookup_dict) for value in obj
        ]
    else:
        return obj


def parse_units(json_ld: dict) -> dict:
    original_context = json_ld.pop('@context')
    key_dict = {'@context': processing_context, 'unit': 'unit', 'value': 'value'}
    # inverse expand-reverse cycle
    expanded = jsonld.expand(key_dict, processing_context)
    compacted = jsonld.compact(expanded, original_context)
    # remove the context
    del compacted['@context']
    # reverse the dict
    original_key_lookup_dict = {v: k for k, v in compacted.items()}
    parsed_json = _replace_units(json_ld, original_context, original_key_lookup_dict)
    parsed_json['@context'] = original_context
    return parsed_json
