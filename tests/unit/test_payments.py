"""Card validation, the fake gateway and the payment form."""

from decimal import Decimal

import pytest

from apps.payments.gateway import APPROVED_TEST_CARD, DECLINED_TEST_CARD, FakeCardGateway
from apps.payments.validators import luhn_valid, normalize_card_number
from apps.web.forms import PaymentForm


@pytest.mark.parametrize("number", [APPROVED_TEST_CARD, DECLINED_TEST_CARD, "5555555555554444"])
def test_luhn_accepts_valid_test_cards(number):
    assert luhn_valid(number)


@pytest.mark.parametrize("number", ["4242424242424241", "1234", "abcd" * 4, ""])
def test_luhn_rejects_invalid_numbers(number):
    assert not luhn_valid(number)


def test_normalize_removes_spaces_and_dashes():
    assert normalize_card_number("4242 4242-4242 4242") == APPROVED_TEST_CARD


def test_fake_gateway_approves_and_declines():
    gateway = FakeCardGateway()

    approved = gateway.charge(amount=Decimal("3"), card_number=APPROVED_TEST_CARD, description="t")
    declined = gateway.charge(amount=Decimal("3"), card_number=DECLINED_TEST_CARD, description="t")

    assert approved.approved and approved.reference.startswith("FAKE-")
    assert not declined.approved


def form(**overrides):
    data = {"customer_name": "Sara", "card_number": "4242 4242 4242 4242", "expiry": "12/40", "cvc": "123"}
    return PaymentForm(data={**data, **overrides})


def test_payment_form_accepts_good_data():
    f = form()

    assert f.is_valid(), f.errors
    assert f.cleaned_data["card_number"] == APPROVED_TEST_CARD


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("customer_name", "   "),
        ("card_number", "4242 4242 4242 4241"),
        ("expiry", "13/40"),
        ("expiry", "01/20"),
        ("cvc", "12"),
    ],
)
def test_payment_form_rejects_bad_data(field, value):
    f = form(**{field: value})

    assert not f.is_valid()
    assert field in f.errors
