"""OrderService: turns the customer's selection into a priced draft and a placed order."""

import secrets
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.menu.models import CoffeeVariant, MilkOption, Size, Syrup
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
    syrup: Syrup | None
    size: Size


def _choice(item) -> Choice:
    return Choice(slug=item.slug, name=item.name, price=item.price)


class OrderService:
    @staticmethod
    def prepare(
        variant_slug: str | None,
        milk_slug: str | None,
        size_slug: str | None,
        syrup_slug: str | None = None,
    ) -> PricedDraft:
        """Look up the selection on the menu, validate it with the builder and price it.

        `syrup_slug` None or "" means no syrup.
        """
        variant = MenuService.variants().filter(slug=variant_slug).first()
        if variant is None:
            raise DraftError("Please choose a coffee first.")
        milk = MenuService.milks().filter(slug=milk_slug).first() if milk_slug else None
        if milk_slug and milk is None:
            raise DraftError("That milk is not available. Please choose another one.")
        syrup = MenuService.syrups().filter(slug=syrup_slug).first() if syrup_slug else None
        if syrup_slug and syrup is None:
            raise DraftError("That syrup is not available. Please choose another one.")
        size = MenuService.sizes().filter(slug=size_slug).first() if size_slug else None

        builder = OrderBuilder().variant(
            _choice(variant), contains_milk=variant.contains_milk, allows_syrup=variant.allows_syrup
        )
        builder.milk(_choice(milk) if milk else None)
        builder.syrup(_choice(syrup) if syrup else None)
        if size is not None:
            builder.size(_choice(size))
        draft = builder.build()

        return PricedDraft(
            draft=draft,
            quote=get_pricing().quote(draft),
            variant=variant,
            milk=milk,
            syrup=syrup,
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
            syrup_name=draft.syrup.name if draft.syrup else "",
            size_name=draft.size.name,
            variant_price=draft.variant.price,
            milk_price=draft.milk.price if draft.milk else 0,
            syrup_price=draft.syrup.price if draft.syrup else 0,
            size_price=draft.size.price,
            total=priced.quote.total,
            picture={
                "image": variant.photo,
                "syrup_color": priced.syrup.color if priced.syrup else None,
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
