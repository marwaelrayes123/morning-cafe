"""Value objects for a coffee order that has not been placed yet."""

from dataclasses import dataclass
from decimal import Decimal

from .money import to_money


@dataclass(frozen=True)
class Choice:
    """One thing the customer picked (a coffee variant, a milk or a size) and its price."""

    slug: str
    name: str
    price: Decimal

    def __post_init__(self):
        price = to_money(self.price)
        if price < 0:
            raise ValueError(f"Price cannot be negative: {self.name}")
        object.__setattr__(self, "price", price)


@dataclass(frozen=True)
class OrderDraft:
    """A complete, validated selection. Build it with `OrderBuilder`."""

    variant: Choice
    size: Choice
    milk: Choice | None = None
    syrup: Choice | None = None
