"""Card number helpers. Card numbers are only checked, never stored or logged."""


def normalize_card_number(raw: str) -> str:
    """Remove spaces and dashes: "4242 4242-4242 4242" -> "4242424242424242"."""
    return "".join(ch for ch in raw if ch not in " -")


def luhn_valid(number: str) -> bool:
    """True if `number` is 12-19 digits and passes the Luhn checksum."""
    if not number.isdigit() or not 12 <= len(number) <= 19:
        return False
    total = 0
    for index, digit in enumerate(int(ch) for ch in reversed(number)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0
