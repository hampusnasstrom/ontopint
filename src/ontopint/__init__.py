import json

import SPARQLWrapper
import rdflib
from pyld import jsonld

# from pint import UnitRegistry
from ucumvert import PintUcumRegistry
import pint

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

def get_ucum_code_from_unit_iri(unit_iri: str) -> str:
    """Fetches the units JSON-LD document from the resolveable `unit_iri`
    and extracts the `ucum_code`

    Parameters
    ----------
    unit_iri
        resolveable IRI of the units JSON-LD document

    Returns
    -------
        the units ucum code

    Example
    -------
    >>> get_ucum_code_from_unit_iri('http://qudt.org/vocab/unit/KiloGM')
    'kg'
    """
    graph = rdflib.Graph()
    graph.parse(unit_iri)
    result = graph.query(
        f'SELECT * WHERE {{<{unit_iri}> <http://qudt.org/schema/qudt/ucumCode> ?ucumCode}}'
    )
    ucum_code = str(result.bindings[0]['ucumCode'])
    return ucum_code 

def get_qunit_iri_from_unit_code(code: str, is_ucum_code: bool = False) -> str:
    """Queries the QUDT SPARQL endpoint to 

    Parameters
    ----------
    code
        the unit code
    is_ucum_code
        Whether the unit code is a http://qudt.org/schema/qudt/symbol (False)
        or a http://qudt.org/schema/qudt/ucumCode (True)


    Returns
    -------
        the units IRI

    Example
    -------
    >>> get_qunit_iri_from_unit_code('kg')
    'http://qudt.org/vocab/unit/KiloGM'
    """
    # testing: https://www.qudt.org/fuseki/#/dataset/qudt/query
    sparql = SPARQLWrapper.SPARQLWrapper("https://www.qudt.org/fuseki/qudt/sparql")

    sparql.setMethod(SPARQLWrapper.POST)
    code = "'" + code + "'"
    query = """
        SELECT ?subject
        WHERE {
            ?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://qudt.org/schema/qudt/Unit> .
            ?subject <{{{predicate}}}> {{{code}}} .
        }
        LIMIT 1
    """.replace(
        "{{{predicate}}}", "http://qudt.org/schema/qudt/ucumCode" if is_ucum_code else "http://qudt.org/schema/qudt/symbol"
    ).replace(
        "{{{code}}}", code + "^^<http://qudt.org/schema/qudt/UCUMcs>" if is_ucum_code else code
    )
    sparql.setQuery(query)
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    result = sparql.query().convert()
    result = result['results']['bindings'][0]['subject']['value']
    return result

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
    
def _serialize_units(obj, context, original_key_lookup_dict):
    if isinstance(obj, dict):
        for key in list(obj.keys()): # make a list copy in order to delete keys while iterating
            value = obj[key]
            if (isinstance(value, pint.Quantity)):
                # see https://pint.readthedocs.io/en/stable/user/formatting.html
                # value = value.to_base_units() # this will not work until we have ucum support
                quantity_value = float(format(value, 'f~').split(' ')[0])
                unit_code = format(value.u, '~') 
                # ToDo: use ucum code
                unit_iri = get_qunit_iri_from_unit_code(unit_code)
                # note: "urn:ontopint:iri" is just any iri not existing in the input data
                unit_compact_iri = jsonld.compact(
                    {"@context": {**context, "urn:ontopint:iri": {"@type": "@id"}}, "urn:ontopint:iri": unit_iri}, 
                    {**context, "urn:ontopint:iri": {"@type": "@id"}}
                )["urn:ontopint:iri"]
                obj[original_key_lookup_dict['value']] = quantity_value
                obj[original_key_lookup_dict['unit']] = unit_compact_iri

            else: obj[key] = _serialize_units(value, context, original_key_lookup_dict)
        return obj
    elif isinstance(obj, list):
        return [
            _serialize_units(value, context, original_key_lookup_dict) for value in obj
        ]
    else:
        return obj


def parse_units(json_ld: dict) -> dict:
    """Replaces keys mapped to `qudt:value` in a nested JSON-LD dict with <pint.Quantity>
    if a unit specification per `qudt:hasUnit` was found on the same level.
    Note: Every nesting needs to maps to some term in the JSON-LD @context.
    This can also be achieved with `@vocab`.

    Parameters
    ----------
    json_ld
        a JSON-LD document as python dict

    Returns
    -------
        a JSON-LD document as python dict with values replaced with <pint.Quantity>

    Examples
    --------
    >>> ontopint.parse_units({
            "@context": {
                "qudt": "http://qudt.org/schema/qudt/",
                "qunit": "http://qudt.org/vocab/unit/",
                "unit": { "@id": "qudt:hasUnit", "@type": "@id" },
                "value": "qudt:value"
            },
            "value": 4.0,
            "unit": "qunit:CentiM"
        })
    {
        '@context': {...},
        'value': <Quantity(4.0, 'centimeter')>
    }
    """

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
    parsed_json = {'@context': original_context, **parsed_json}
    json_ld['@context'] = original_context # restore context
    return parsed_json

def export_units(json_ld: dict, context = processing_context) -> dict:
    """Replaces the value of keys mapped to `qudt:value` in a nested JSON-LD dict
    if they are of type <pint.Quantity> with their plain numeric value
    while a unit specification per `qudt:hasUnit` is generated on the same level.
    Note: Every nesting needs to maps to some term in the JSON-LD @context.
    This can also be achieved with `@vocab`.

    Parameters
    ----------
    json_ld
        a JSON-LD document as python dict with values of type <pint.Quantity>

    Returns
    -------
        a JSON-LD document as python dict with values as plain floats and a unit
        specification per `qudt:hasUnit`

    Examples
    --------
    >>> ontopint.parse_units({
            '@context': {...},
            'value': <Quantity(4.0, 'centimeter')>
        })
    {
        '@context': {
            'qudt': 'http://qudt.org/schema/qudt/',
            'qunit': 'http://qudt.org/vocab/unit/',
            'unit': { '@id': 'qudt:hasUnit', '@type': '@id' },
            'value': 'qudt:value'
        },
        'value': 4.0,
        'unit': 'qunit:CentiM'
    }
    """
    
    original_context = json_ld.pop('@context', context)
    key_dict = {'@context': processing_context, 'unit': 'unit', 'value': 'value'}
    # inverse expand-reverse cycle
    expanded = jsonld.expand(key_dict, processing_context)
    compacted = jsonld.compact(expanded, original_context)
    # remove the context
    del compacted['@context']
    # reverse the dict
    original_key_lookup_dict = {v: k for k, v in compacted.items()}
    parsed_json = _serialize_units(json_ld, original_context, original_key_lookup_dict)
    parsed_json = {'@context': original_context, **parsed_json}
    json_ld['@context'] = original_context # restore context
    return parsed_json
