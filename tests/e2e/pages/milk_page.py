from .base_page import BasePage, starts_with


class MilkPage(BasePage):
    path = "/order/milk/"

    def choose(self, milk: str):
        """Returns SyrupPage (if the drink can have syrup) or SizePage."""
        self.page.get_by_role("button", name=starts_with(milk)).click()
        return self._next_order_step()
