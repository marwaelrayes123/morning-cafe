"""Service layer: MenuService, OrderService, PaymentService (uses the test database)."""

from decimal import Decimal

import pytest

from apps.menu.models import CoffeeVariant
from apps.menu.seed import seed_menu
from apps.menu.services import MenuService
from apps.ordering.builder import DraftError
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.payments.gateway import APPROVED_TEST_CARD, DECLINED_TEST_CARD
from apps.payments.models import Payment
from apps.payments.services import PaymentError, PaymentService

pytestmark = pytest.mark.django_db


def test_seed_is_idempotent(menu):
    seed_menu()

    assert MenuService.coffees().count() == 7
    assert CoffeeVariant.objects.count() == 20
    assert MenuService.syrups().count() == 5
    assert MenuService.milks().count() == 6
    assert MenuService.sizes().count() == 3


def test_coffees_have_a_from_price(menu):
    latte = MenuService.coffees().get(slug="latte")

    assert latte.from_price == Decimal("48.00")


def test_unavailable_variants_are_hidden(menu):
    CoffeeVariant.objects.filter(slug="doppio").update(is_available=False)

    assert not MenuService.variants().filter(slug="doppio").exists()


def test_prepare_prices_a_milk_coffee(menu):
    priced = OrderService.prepare("classic-latte", "oat-milk", "large", "caramel")

    assert priced.quote.total == Decimal("73.00")  # 48 + 6 + 5 + 14 kr.
    assert [line.label for line in priced.quote.lines] == [
        "Classic Latte",
        "Oat milk",
        "Caramel syrup",
        "Size: Large",
    ]


def test_prepare_rejects_syrup_in_an_espresso(menu):
    with pytest.raises(DraftError, match="without syrup"):
        OrderService.prepare("doppio", None, "small", "vanilla")


def test_order_remembers_the_syrup_bottle(menu):
    order = OrderService.place_order(OrderService.prepare("classic-latte", "oat-milk", "small", "lavender"))

    assert (order.syrup_name, order.syrup_price) == ("Lavender", Decimal("5.00"))
    assert order.syrup_color == "#8e6cc0"
    assert ("Lavender syrup", Decimal("5.00")) in order.price_lines


def test_prepare_requires_milk_for_milk_coffee(menu):
    with pytest.raises(DraftError, match="milk"):
        OrderService.prepare("classic-latte", None, "large")


def test_prepare_rejects_unknown_coffee(menu):
    with pytest.raises(DraftError):
        OrderService.prepare("tea", None, "small")


def test_place_order_copies_names_and_prices(menu):
    order = OrderService.place_order(OrderService.prepare("doppio", None, "medium"))

    assert order.status == Order.Status.PENDING
    assert order.number.startswith("MC-")
    assert (order.variant_name, order.milk_name, order.size_name) == ("Doppio", "", "Medium")
    assert order.total == Decimal("46.00")  # 38 + 8 kr.
    assert order.photo == "web/img/coffee/espresso.jpg"  # standard espresso-cup photo


def test_approved_payment_marks_order_paid(menu):
    order = OrderService.place_order(OrderService.prepare("classic-latte", "whole-milk", "small"))

    payment = PaymentService().pay(order, customer_name="Sara", card_number=APPROVED_TEST_CARD)

    order.refresh_from_db()
    assert payment.status == Payment.Status.APPROVED
    assert payment.card_last4 == "4242"
    assert order.is_paid and order.customer_name == "Sara" and order.paid_at


def test_declined_payment_marks_order_failed_and_allows_retry(menu):
    order = OrderService.place_order(OrderService.prepare("classic-latte", "whole-milk", "small"))

    PaymentService().pay(order, customer_name="Sara", card_number=DECLINED_TEST_CARD)
    assert order.status == Order.Status.FAILED

    PaymentService().pay(order, customer_name="Sara", card_number=APPROVED_TEST_CARD)
    assert order.is_paid


def test_cannot_pay_twice(menu):
    order = OrderService.place_order(OrderService.prepare("doppio", None, "small"))
    PaymentService().pay(order, customer_name="Sara", card_number=APPROVED_TEST_CARD)

    with pytest.raises(PaymentError):
        PaymentService().pay(order, customer_name="Sara", card_number=APPROVED_TEST_CARD)


def test_order_is_ready_after_prep_time(menu, settings):
    settings.COFFEE_PREP_SECONDS = 10
    order = OrderService.place_order(OrderService.prepare("doppio", None, "small"))
    PaymentService().pay(order, customer_name="Sara", card_number=APPROVED_TEST_CARD)

    assert not order.is_ready()
    assert order.is_ready(now=order.ready_at)
