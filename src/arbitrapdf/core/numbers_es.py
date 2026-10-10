from __future__ import annotations

_UNITS = {
    0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro",
    5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve",
    10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
    15: "quince", 16: "dieciséis", 17: "diecisiete", 18: "dieciocho",
    19: "diecinueve", 20: "veinte", 21: "veintiuno", 22: "veintidós",
    23: "veintitrés", 24: "veinticuatro", 25: "veinticinco",
    26: "veintiséis", 27: "veintisiete", 28: "veintiocho", 29: "veintinueve",
}
_TENS = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"}
_HUNDREDS = {200: "doscientos", 300: "trescientos", 400: "cuatrocientos", 500: "quinientos", 600: "seiscientos", 700: "setecientos", 800: "ochocientos", 900: "novecientos"}


def _under_100(n: int) -> str:
    if n < 30:
        return _UNITS[n]
    tens = (n // 10) * 10
    unit = n % 10
    return _TENS[tens] if unit == 0 else f"{_TENS[tens]} y {_UNITS[unit]}"


def _under_1000(n: int) -> str:
    if n < 100:
        return _under_100(n)
    if n == 100:
        return "cien"
    if n < 200:
        return f"ciento {_under_100(n - 100)}"
    hundreds = (n // 100) * 100
    rest = n % 100
    return _HUNDREDS[hundreds] if rest == 0 else f"{_HUNDREDS[hundreds]} {_under_100(rest)}"


def _apocopate_one(text: str) -> str:
    if text.endswith("veintiuno"):
        return text[:-9] + "veintiún"
    if text.endswith(" y uno"):
        return text[:-5] + " y un"
    if text.endswith("uno"):
        return text[:-3] + "un"
    return text


def integer_to_spanish(n: int) -> str:
    """Convert an integer from 0 through 999,999,999 to Spanish words."""
    if not isinstance(n, int):
        raise TypeError("n debe ser un entero")
    if n < 0 or n > 999_999_999:
        raise ValueError("Solo se admiten valores entre 0 y 999,999,999")
    if n < 1000:
        return _under_1000(n)

    millions, rest = divmod(n, 1_000_000)
    parts: list[str] = []
    if millions:
        if millions == 1:
            parts.append("un millón")
        else:
            parts.append(f"{_apocopate_one(integer_to_spanish(millions))} millones")

    thousands, units = divmod(rest, 1000)
    if thousands:
        if thousands == 1:
            parts.append("mil")
        else:
            parts.append(f"{_apocopate_one(_under_1000(thousands))} mil")

    if units:
        parts.append(_under_1000(units))

    return " ".join(parts)
