"""Domain layer: OrderBuilder + pricing. Pure Python, no database."""

from decimal import Decimal

import pytest

from apps.ordering.builder import DraftError, OrderBuilder
from apps.ordering.draft import Choice
from apps.ordering.money import to_money
from apps.ordering.pricing import get_pricing

LATTE = Choice("caramel-latte", "Caramel Latte", Decimal("3.90"))
ESPRESSO = Choice("doppio", "Doppio", Decimal("2.80"))
OAT = Choice("oat-milk", "Oat milk", Decimal("0.50"))
LARGE = Choice("large", "Large", Decimal("1.10"))
VANILLA = Choice("vanilla", "Vanilla", Decimal("0.60"))
SMALL = Choice("small", "Small", Decimal("0"))


def test_builds_a_milk_coffee():
    draft = OrderBuilder().variant(LATTE, contains_milk=True).milk(OAT).size(LARGE).build()

    assert draft.variant == LATTE
    assert draft.milk == OAT
    assert draft.size == LARGE


def test_builds_a_coffee_without_milk():
    draft = OrderBuilder().variant(ESPRESSO, contains_milk=False).size(SMALL).build()

    assert draft.milk is None


@pytest.mark.parametrize(
    ("builder", "message"),
    [
        (OrderBuilder().size(SMALL), "choose a coffee"),
        (OrderBuilder().variant(LATTE, contains_milk=True).size(SMALL), "type of milk"),
        (OrderBuilder().variant(ESPRESSO, contains_milk=False).milk(OAT).size(SMALL), "without milk"),
        (OrderBuilder().variant(LATTE, contains_milk=True).milk(OAT), "choose a size"),
    ],
)
def test_rejects_incomplete_or_wrong_selection(builder, message):
    with pytest.raises(DraftError, match=message):
        builder.build()


def test_price_is_coffee_plus_milk_plus_size():
    draft = OrderBuilder().variant(LATTE, contains_milk=True).milk(OAT).size(LARGE).build()

    quote = get_pricing().quote(draft)

    assert [(line.label, line.amount) for line in quote.lines] == [
        ("Caramel Latte", Decimal("3.90")),
        ("Oat milk", Decimal("0.50")),
        ("Size: Large", Decimal("1.10")),
    ]
    assert quote.total == Decimal("5.50")


def test_syrup_adds_its_own_price_line():
    draft = (
        OrderBuilder()
        .variant(LATTE, contains_milk=True, allows_syrup=True)
        .milk(OAT)
        .syrup(VANILLA)
        .size(LARGE)
        .build()
    )

    quote = get_pricing().quote(draft)

    assert [line.label for line in quote.lines] == [
        "Caramel Latte",
        "Oat milk",
        "Vanilla syrup",
        "Size: Large",
    ]
    assert quote.total == Decimal("6.10")


def test_syrup_is_rejected_when_not_allowed():
    builder = (
        OrderBuilder().variant(ESPRESSO, contains_milk=False, allows_syrup=False).syrup(VANILLA).size(SMALL)
    )

    with pytest.raises(DraftError, match="without syrup"):
        builder.build()


def test_price_without_milk_has_no_milk_line():
    draft = OrderBuilder().variant(ESPRESSO, contains_milk=False).size(SMALL).build()

    quote = get_pricing().quote(draft)

    assert [line.label for line in quote.lines] == ["Doppio", "Size: Small"]
    assert quote.total == Decimal("2.80")


def test_choice_rejects_negative_price():
    with pytest.raises(ValueError):
        Choice("x", "X", Decimal("-1"))


def test_money_rounds_half_up_to_cents():
    assert to_money("3.905") == Decimal("3.91")
    assert to_money(2) == Decimal("2.00")
