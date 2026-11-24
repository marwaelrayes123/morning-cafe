"""Builder pattern: assemble an OrderDraft step by step, then validate it once in build()."""

from typing import Self

from .draft import Choice, OrderDraft


class DraftError(ValueError):
    """The selection is incomplete or does not make sense."""


class OrderBuilder:
    def __init__(self) -> None:
        self._variant: Choice | None = None
        self._contains_milk = False
        self._milk: Choice | None = None
        self._size: Choice | None = None

    def variant(self, choice: Choice, *, contains_milk: bool) -> Self:
        self._variant = choice
        self._contains_milk = contains_milk
        return self

    def milk(self, choice: Choice | None) -> Self:
        self._milk = choice
        return self

    def size(self, choice: Choice) -> Self:
        self._size = choice
        return self

    def build(self) -> OrderDraft:
        if self._variant is None:
            raise DraftError("Please choose a coffee first.")
        if self._contains_milk and self._milk is None:
            raise DraftError("Please choose a type of milk.")
        if not self._contains_milk and self._milk is not None:
            raise DraftError(f"{self._variant.name} is made without milk.")
        if self._size is None:
            raise DraftError("Please choose a size.")
        return OrderDraft(variant=self._variant, milk=self._milk, size=self._size)
