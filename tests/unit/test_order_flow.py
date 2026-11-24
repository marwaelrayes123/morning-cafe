"""The web pages, clicked through with Django's test client."""

import pytest
from django.urls import reverse

from apps.orders.models import Order

pytestmark = pytest.mark.django_db

CARD = {"customer_name": "Sara", "card_number": "4242 4242 4242 4242", "expiry": "12/40", "cvc": "123"}


def test_menu_lists_coffee_types(client, menu):
    html = client.get(reverse("web:menu")).content.decode()

    for name in ("Espresso", "Latte", "Cappuccino", "Mocha", "Iced Coffee"):
        assert name in html
    assert "from €3.60" in html  # Latte


def test_coffee_page_lists_sub_categories(client, menu):
    html = client.get(reverse("web:coffee", args=["latte"])).content.decode()

    for name in ("Classic Latte", "Vanilla Latte", "Caramel Latte", "Hazelnut Latte"):
        assert name in html


def test_full_order_with_milk(client, menu, instant_prep):
    # Sub-category with milk -> milk step
    response = client.post(reverse("web:order_start"), {"variant": "caramel-latte"})
    assert response.url == reverse("web:order_milk")
    assert "Oat milk" in client.get(response.url).content.decode()

    response = client.post(reverse("web:order_milk"), {"milk": "oat-milk"})
    assert response.url == reverse("web:order_size")

    response = client.post(reverse("web:order_size"), {"size": "large"})
    assert response.url == reverse("web:order_review")

    # The price is shown before paying
    review = client.get(reverse("web:order_review")).content.decode()
    assert "€5.50" in review and "Agree &amp; pay" in review

    response = client.post(reverse("web:order_review"))
    order = Order.objects.get()
    assert response.url == reverse("web:order_pay", args=[order.number])

    response = client.post(response.url, CARD)
    assert response.url == reverse("web:order_preparing", args=[order.number])

    # Prep time is 0 in this test, so "preparing" sends us straight to "ready"
    response = client.get(response.url)
    assert response.url == reverse("web:order_ready", args=[order.number])

    ready = client.get(response.url).content.decode()
    assert "Your Caramel Latte is ready, Sara!" in ready
    assert order.number in ready


def test_coffee_without_milk_skips_the_milk_step(client, menu):
    response = client.post(reverse("web:order_start"), {"variant": "doppio"})

    assert response.url == reverse("web:order_size")
    assert client.get(reverse("web:order_milk")).url == reverse("web:order_size")


def test_review_without_a_selection_goes_back_to_menu(client, menu):
    response = client.get(reverse("web:order_review"))

    assert response.url == reverse("web:menu")


def test_preparing_page_shows_while_coffee_is_made(client, menu, settings):
    settings.COFFEE_PREP_SECONDS = 30
    client.post(reverse("web:order_start"), {"variant": "doppio"})
    client.post(reverse("web:order_size"), {"size": "small"})
    client.post(reverse("web:order_review"))
    order = Order.objects.get()
    client.post(reverse("web:order_pay", args=[order.number]), CARD)

    html = client.get(reverse("web:order_preparing", args=[order.number])).content.decode()

    assert "Preparing your Doppio" in html
    assert 'http-equiv="refresh"' in html
    # Not ready yet -> the ready page sends you back
    assert client.get(reverse("web:order_ready", args=[order.number])).url.endswith("/preparing/")


def test_declined_card_shows_error_and_stays_on_pay_page(client, menu):
    client.post(reverse("web:order_start"), {"variant": "doppio"})
    client.post(reverse("web:order_size"), {"size": "small"})
    client.post(reverse("web:order_review"))
    order = Order.objects.get()

    response = client.post(
        reverse("web:order_pay", args=[order.number]), {**CARD, "card_number": "4000 0000 0000 0002"}
    )

    assert response.status_code == 200
    assert "declined" in response.content.decode()
    order.refresh_from_db()
    assert order.status == Order.Status.FAILED
