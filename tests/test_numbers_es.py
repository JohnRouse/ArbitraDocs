from arbitrapdf.core.numbers_es import integer_to_spanish


def test_examples():
    assert integer_to_spanish(0) == "cero"
    assert integer_to_spanish(100) == "cien"
    assert integer_to_spanish(101) == "ciento uno"
    assert integer_to_spanish(1000) == "mil"
    assert integer_to_spanish(13220) == "trece mil doscientos veinte"
    assert integer_to_spanish(21000) == "veintiún mil"
    assert integer_to_spanish(1_000_000) == "un millón"
    assert integer_to_spanish(21_000_000) == "veintiún millones"
