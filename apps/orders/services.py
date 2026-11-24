"""OrderService: turns the customer's selection into a priced draft and a placed order."""

import secrets
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.menu.models import CoffeeVariant, MilkOption, Size
from apps.menu.services import MenuService
from apps.ordering.builder import DraftError, OrderBuilder
from apps.ordering.draft import Choice, OrderDraft
from apps.ordering.pricing import Quote, get_pricing

from .models import Order

NUMBER_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O or 1/I mix-ups


@dataclass(frozen=True)
class PricedDraft:
    """Everything the review page needs: the validated draft, its price and the menu rows."""

    draft: OrderDraft
    quote: Quote
    variant: CoffeeVariant
    milk: MilkOption | None
    size: Size


def _choice(item) -> Choice:
    return Choice(slug=item.slug, name=item.name, price=item.price)


class OrderService:
    @staticmethod
    def prepare(variant_slug: str | None, milk_slug: str | None, size_slug: str | None) -> PricedDraft:
        """Look up the selection on the menu, validate it with the builder and price it."""
        variant = MenuService.variants().filter(slug=variant_slug).first()
        if variant is None:
            raise DraftError("Please choose a coffee first.")
        milk = MenuService.milks().filter(slug=milk_slug).first() if milk_slug else None
        if milk_slug and milk is None:
            raise DraftError("That milk is not available. Please choose another one.")
        size = MenuService.sizes().filter(slug=size_slug).first() if size_slug else None

        builder = OrderBuilder().variant(_choice(variant), contains_milk=variant.contains_milk)
        builder.milk(_choice(milk) if milk else None)
        if size is not None:
            builder.size(_choice(size))
        draft = builder.build()

        return PricedDraft(
            draft=draft,
            quote=get_pricing().quote(draft),
            variant=variant,
            milk=milk,
            size=size,
        )

    @staticmethod
    @transaction.atomic
    def place_order(priced: PricedDraft) -> Order:
        """Save the draft as a pending order (prices copied in) and return it."""
        draft, variant = priced.draft, priced.variant
        return Order.objects.create(
            number=OrderService._new_number(),
            variant=variant,
            coffee_name=variant.coffee.name,
            variant_name=draft.variant.name,
            milk_name=draft.milk.name if draft.milk else "",
            size_name=draft.size.name,
            variant_price=draft.variant.price,
            milk_price=draft.milk.price if draft.milk else 0,
            size_price=draft.size.price,
            total=priced.quote.total,
            picture={
                "layers": variant.layers,
                "iced": variant.is_iced,
                "milk_color": priced.milk.color if priced.milk else None,
            },
        )

    @staticmethod
    def mark_paid(order: Order, customer_name: str) -> Order:
        order.status = Order.Status.PAID
        order.customer_name = customer_name
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "customer_name", "paid_at"])
        return order

    @staticmethod
    def mark_failed(order: Order) -> Order:
        order.status = Order.Status.FAILED
        order.save(update_fields=["status"])
        return order

    @staticmethod
    def _new_number() -> str:
        while True:
            number = "MC-" + "".join(secrets.choice(NUMBER_ALPHABET) for _ in range(5))
            if not Order.objects.filter(number=number).exists():
                return number
