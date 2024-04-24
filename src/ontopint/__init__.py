import json
import rdflib
from pint import UnitRegistry

ureg = UnitRegistry()

class UnitDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'unit' in obj and 'value' in obj:
            return ureg.Quantity(obj['value'], obj['unit'])
        unit = None
        unit_defs = [v for k, v in obj.items() if isinstance(v, str) and v.startswith('qudt:')]
        if len(unit_defs) > 1:
            raise ValueError('More that one unit definition')
        if unit_defs:
            iri = unit_defs[0].replace('qudt:', 'http://qudt.org/vocab/unit/')
            graph = rdflib.Graph()
            graph.parse(iri)
            result = graph.query(f"SELECT * WHERE {{<{iri}> <http://qudt.org/schema/qudt/symbol> ?symbol}}")
            unit = result.bindings[0]['symbol']
            for k, v in obj.items():
                if isinstance(v, float):
                    obj[k] = ureg.Quantity(v, unit)
        return obj
