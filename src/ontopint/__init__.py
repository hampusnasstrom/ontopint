import json

import rdflib
from pyld import jsonld
from pint import UnitRegistry

ureg = UnitRegistry()


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


def _replace_units(obj, context):
    if isinstance(obj, dict):
        if 'unit' in obj and 'value' in obj:
            expanded_obj = jsonld.expand({**obj, '@context': context}, context)
            unit_iri = expanded_obj[0]['http://qudt.org/schema/qudt/hasUnit'][0]['@id']
            obj.pop('unit')
            graph = rdflib.Graph()
            graph.parse(unit_iri)
            result = graph.query(
                f'SELECT * WHERE {{<{unit_iri}> <http://qudt.org/schema/qudt/symbol> ?symbol}}'
            )
            unit = result.bindings[0]['symbol']
            obj['value'] = ureg.Quantity(obj['value'], unit)

        for key, value in obj.items():
            obj[key] = _replace_units(value, context)
        return obj
    elif isinstance(obj, list):
        return [_replace_units(value, context) for value in obj]
    else:
        return obj


def parse_units(json_ld: dict) -> dict:
    original_context = json_ld.pop('@context')
    parsed_json = _replace_units(json_ld, original_context)
    parsed_json['@context'] = original_context
    return parsed_json
