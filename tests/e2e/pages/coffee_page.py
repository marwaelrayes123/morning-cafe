from .base_page import BasePage, starts_with


class CoffeePage(BasePage):
    """Sub-categories of one coffee type."""

    def variant_names(self) -> list[str]:
        return self.page.locator(".option-title").all_inner_texts()

    def choose(self, variant: str):
        """Returns MilkPage for coffees with milk, otherwise SizePage."""
        from .milk_page import MilkPage
        from .size_page import SizePage

        self.page.get_by_role("button", name=starts_with(variant)).click()
        self.page.wait_for_load_state()
        if self.page.url.endswith("/order/milk/"):
            return MilkPage(self.page, self.base_url)
        return SizePage(self.page, self.base_url)
