"""Prices are shown in Danish kroner the Danish way."""

from decimal import Decimal

import pytest

from apps.web.templatetags.cafe import format_money, money


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("52.00"), "52 kr."),
        (Decimal("52.50"), "52,50 kr."),
        (Decimal("0"), "0 kr."),
        (Decimal("1250.00"), "1.250 kr."),
        (Decimal("1250.75"), "1.250,75 kr."),
    ],
)
def test_danish_kroner_format(value, expected):
    assert format_money(value, "DKK") == expected


def test_other_currencies_still_work():
    assert format_money(Decimal("3.9"), "EUR") == "€3.90"


def test_filter_uses_shop_currency_and_optional_sign(settings):
    settings.CAFE_CURRENCY = "DKK"

    assert money(Decimal("6")) == "6 kr."
    assert money(Decimal("6"), "+") == "+ 6 kr."
    assert money(None) == ""
