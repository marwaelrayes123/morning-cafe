from .base_page import BasePage, starts_with
from .size_page import SizePage


class MilkPage(BasePage):
    path = "/order/milk/"

    def choose(self, milk: str) -> SizePage:
        self.page.get_by_role("button", name=starts_with(milk)).click()
        return SizePage(self.page, self.base_url)
