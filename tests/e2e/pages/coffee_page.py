from .base_page import BasePage, starts_with


class CoffeePage(BasePage):
    """Sub-categories of one coffee type."""

    def variant_names(self) -> list[str]:
        return self.page.locator(".option-title").all_inner_texts()

    def choose(self, variant: str):
        """Returns MilkPage, SyrupPage or SizePage, depending on the drink."""
        self.page.get_by_role("button", name=starts_with(variant)).click()
        return self._next_order_step()
