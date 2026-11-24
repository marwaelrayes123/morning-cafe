import re

import pytest
from playwright.sync_api import expect

from tests.e2e.data import APPROVED_CARD, CUSTOMER, CVC, DECLINED_CARD, EXPIRY

pytestmark = pytest.mark.e2e


def test_menu_lists_coffee_types(home_page):
    menu = home_page.open().go_to_menu()

    assert {"Espresso", "Latte", "Cappuccino", "Mocha"} <= set(menu.coffee_names())


def test_order_latte_with_oat_milk_and_caramel_from_menu_to_pickup(home_page):
    coffee = home_page.open().go_to_menu().choose("Latte")
    assert "Classic Latte" in coffee.variant_names()

    syrup = coffee.choose("Classic Latte").choose("Oat milk")
    assert "Caramel" in syrup.syrup_names()
    review = syrup.choose("Caramel").choose("Large")

    # The price is shown before the customer agrees, with the chosen syrup bottle
    assert review.line_items() == ["Classic Latte", "Oat milk", "Caramel syrup", "Size: Large"]
    expect(review.total()).to_have_text("73 kr.")
    expect(review.syrup_bottle()).to_be_visible()

    preparing = review.agree_and_pay().pay(CUSTOMER, APPROVED_CARD, EXPIRY, CVC)
    expect(preparing.heading()).to_have_text("Preparing your Classic Latte…")

    ready = preparing.wait_until_ready()
    expect(ready.heading()).to_have_text(f"Your Classic Latte is ready, {CUSTOMER}!")
    assert re.fullmatch(r"MC-[A-Z0-9]{5}", ready.order_number())


def test_coffee_without_milk_skips_milk_and_declined_card_can_retry(home_page):
    review = home_page.open().go_to_menu().choose("Espresso").choose("Doppio").choose("Small")
    expect(review.total()).to_have_text("38 kr.")

    payment = review.agree_and_pay()
    payment.fill(CUSTOMER, DECLINED_CARD, EXPIRY, CVC)
    expect(payment.error_message()).to_contain_text("declined")

    ready = payment.pay(CUSTOMER, APPROVED_CARD, EXPIRY, CVC).wait_until_ready()
    expect(ready.heading()).to_have_text(f"Your Doppio is ready, {CUSTOMER}!")
