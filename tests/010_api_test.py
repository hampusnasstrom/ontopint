
import pint
from ontopint import get_qunit_iri_from_unit_code, get_ucum_code_from_unit_iri
import ontopint

def test_pint_print_formats():
    # see https://pint.readthedocs.io/en/stable/user/formatting.html
    q : pint.Quantity = pint.Quantity(1.0, ontopint.ureg.from_ucum("kg"))
    assert( float(format(q, 'f#~').split(' ')[0]) == 1.0)
    assert( format(q.u, '~') == "kg") 

def test_qudt_sparql_api():
    assert (get_qunit_iri_from_unit_code("kg") == "http://qudt.org/vocab/unit/KiloGM")
    assert (get_qunit_iri_from_unit_code("kg", True) == "http://qudt.org/vocab/unit/KiloGM")
    assert (get_ucum_code_from_unit_iri("http://qudt.org/vocab/unit/KiloGM") == "kg")