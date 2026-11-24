"""Payment gateways. The app depends on the `PaymentGateway` interface, so a real
provider could be added later without touching the services or views."""

import secrets
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

APPROVED_TEST_CARD = "4242424242424242"
DECLINED_TEST_CARD = "4000000000000002"


@dataclass(frozen=True)
class ChargeResult:
    approved: bool
    reference: str
    message: str


class PaymentGateway(Protocol):
    def charge(self, *, amount: Decimal, card_number: str, description: str) -> ChargeResult: ...


class FakeCardGateway:
    """No real money. The declined test card is declined; every other valid card is approved."""

    def charge(self, *, amount: Decimal, card_number: str, description: str) -> ChargeResult:
        reference = "FAKE-" + secrets.token_hex(4).upper()
        if card_number == DECLINED_TEST_CARD:
            return ChargeResult(False, reference, "Your card was declined. Please try another card.")
        return ChargeResult(True, reference, "Payment approved.")


def get_payment_gateway() -> PaymentGateway:
    """Factory: the one place that decides which gateway is used."""
    return FakeCardGateway()
