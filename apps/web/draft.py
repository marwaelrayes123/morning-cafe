"""Keeps the customer's in-progress selection (coffee variant, milk, size) in the browser session.

It stores slugs only; prices are always looked up fresh from the menu by OrderService.
"""

from dataclasses import dataclass

SESSION_KEY = "order_draft"


@dataclass
class DraftSelection:
    variant: str | None = None
    milk: str | None = None
    size: str | None = None


class DraftSession:
    def __init__(self, session) -> None:
        self._session = session

    def get(self) -> DraftSelection:
        return DraftSelection(**self._session.get(SESSION_KEY, {}))

    def start(self, variant_slug: str) -> None:
        """A new coffee was picked: forget any earlier milk/size choice."""
        self._save(DraftSelection(variant=variant_slug))

    def set_milk(self, milk_slug: str) -> None:
        selection = self.get()
        selection.milk = milk_slug
        self._save(selection)

    def set_size(self, size_slug: str) -> None:
        selection = self.get()
        selection.size = size_slug
        self._save(selection)

    def clear(self) -> None:
        self._session.pop(SESSION_KEY, None)

    def _save(self, selection: DraftSelection) -> None:
        self._session[SESSION_KEY] = selection.__dict__.copy()
