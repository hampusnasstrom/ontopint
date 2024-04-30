
import pint
from ontopint import get_qunit_iri_from_unit_code, get_ucum_code_from_unit_iri
import ontopint

def test_pint_print_formats():
    # see https://pint.readthedocs.io/en/stable/user/formatting.html
    q : pint.Quantity = pint.Quantity(1.0, ontopint.ureg.from_ucum("kg")).to_base_units()
    assert( float(format(q, 'f~').split(' ')[0]) == 1.0)
    assert( format(q.u, '~') == "kg")
    q : pint.Quantity = pint.Quantity(304, ontopint.ureg.from_ucum("cm"))
    assert( float(format(q, 'f~').split(' ')[0]) == 304)
    assert( format(q, 'f~').split(' ')[1] == "cm")
    q : pint.Quantity = pint.Quantity(10, ontopint.ureg.from_ucum("eV"))
    assert( float(format(q, 'f~').split(' ')[0]) == 10)
    assert( format(q.u, '~') == "eV") 

def test_qudt_sparql_api():
    assert (get_qunit_iri_from_unit_code("kg") == "http://qudt.org/vocab/unit/KiloGM")
    assert (get_qunit_iri_from_unit_code("kg", True) == "http://qudt.org/vocab/unit/KiloGM")
    assert (get_ucum_code_from_unit_iri("http://qudt.org/vocab/unit/KiloGM") == "kg")

    assert (get_qunit_iri_from_unit_code("m") == "http://qudt.org/vocab/unit/M")
    assert (get_qunit_iri_from_unit_code("m", True) == "http://qudt.org/vocab/unit/M")