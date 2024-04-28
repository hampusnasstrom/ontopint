# ontopint
A python package for reading & writing units from a JSON-LD files and generating pint quantities.

## How it works

```python
import ontopint

# jsonld input with 'value' and 'unit' mapped to qudt terms
data = {
  "@context": {
    "qudt": "http://qudt.org/schema/qudt/",
    "qunit": "http://qudt.org/vocab/unit/",
    "qkind": "http://qudt.org/vocab/quantkind/",
    "unit": {
      "@id": "qudt:hasUnit",
      "@type": "@id"
    },
    "quantity": {
      "@id": "qudt:hasQuantityKind",
      "@type": "@id"
    },
    "value": "qudt:value"
  },
  "value": 4.0,
  "unit": "qunit:CentiM"
}

# convert the value + unit pairs to pint.Quantity
data = ontopint.parse_units(data)
print(data)
"""
{
  '@context': {...},
  'value': <Quantity(4.0, 'centimeter')>
}
"""

# do something with pint
data["value"] += 3 * ontopint.ureg.meter
data["value"] = data["value"].to(ontopint.ureg.meter)
print(data)
"""
{
  '@context': {...},
  'value': <Quantity(3.04, 'meter')>
}
"""

# export the result as jsonld
data = ontopint.export_units(data)
print(data)
"""
{
  "@context": {
    "qudt": "http://qudt.org/schema/qudt/",
    "qunit": "http://qudt.org/vocab/unit/",
    "qkind": "http://qudt.org/vocab/quantkind/",
    "unit": {
      "@id": "qudt:hasUnit",
      "@type": "@id"
    },
    "quantity": {
      "@id": "qudt:hasQuantityKind",
      "@type": "@id"
    },
    "value": "qudt:value"
  },
  "value": 3.04,
  "unit": "qunit:M"
}
"""
```

Note: more complex examples can be found at [tests/data](https://github.com/hampusnasstrom/ontopint/tree/main/tests/data)
