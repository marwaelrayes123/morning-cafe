"""Strategy pattern for pricing. Add a new rule (e.g. happy hour) as a new class."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from .draft import OrderDraft
from .money import to_money


@dataclass(frozen=True)
class QuoteLine:
    label: str
    amount: Decimal


@dataclass(frozen=True)
class Quote:
    lines: tuple[QuoteLine, ...]

    @property
    def total(self) -> Decimal:
        return to_money(sum((line.amount for line in self.lines), Decimal("0")))


class PricingStrategy(Protocol):
    def quote(self, draft: OrderDraft) -> Quote: ...


class StandardPricing:
    """Coffee price + milk price (if any) + size price."""

    def quote(self, draft: OrderDraft) -> Quote:
        lines = [QuoteLine(draft.variant.name, draft.variant.price)]
        if draft.milk is not None:
            lines.append(QuoteLine(draft.milk.name, draft.milk.price))
        lines.append(QuoteLine(f"Size: {draft.size.name}", draft.size.price))
        return Quote(tuple(lines))


def get_pricing() -> PricingStrategy:
    """Factory: the one place that decides which pricing rules are active."""
    return StandardPricing()
