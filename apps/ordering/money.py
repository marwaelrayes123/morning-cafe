"""Money helpers. Always Decimal, never float."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def to_money(value: Decimal | int | str) -> Decimal:
    """Round to whole cents (half-up), e.g. to_money("3.905") -> Decimal("3.91")."""
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)
