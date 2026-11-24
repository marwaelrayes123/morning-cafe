"""Builder pattern: assemble an OrderDraft step by step, then validate it once in build()."""

from typing import Self

from .draft import Choice, OrderDraft


class DraftError(ValueError):
    """The selection is incomplete or does not make sense."""


class OrderBuilder:
    def __init__(self) -> None:
        self._variant: Choice | None = None
        self._contains_milk = False
        self._allows_syrup = False
        self._milk: Choice | None = None
        self._syrup: Choice | None = None
        self._size: Choice | None = None

    def variant(self, choice: Choice, *, contains_milk: bool, allows_syrup: bool = False) -> Self:
        self._variant = choice
        self._contains_milk = contains_milk
        self._allows_syrup = allows_syrup
        return self

    def milk(self, choice: Choice | None) -> Self:
        self._milk = choice
        return self

    def syrup(self, choice: Choice | None) -> Self:
        """Optional: None means no syrup."""
        self._syrup = choice
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
        if not self._allows_syrup and self._syrup is not None:
            raise DraftError(f"{self._variant.name} is served without syrup.")
        if self._size is None:
            raise DraftError("Please choose a size.")
        return OrderDraft(variant=self._variant, milk=self._milk, syrup=self._syrup, size=self._size)
