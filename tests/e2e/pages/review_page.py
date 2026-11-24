import re

from playwright.sync_api import Locator

from .base_page import BasePage
from .payment_page import PaymentPage


class ReviewPage(BasePage):
    """Shows the price before the customer agrees to pay."""

    path = "/order/review/"

    def line_items(self) -> list[str]:
        return self.page.get_by_test_id("price-lines").locator("tbody th").all_inner_texts()

    def total(self) -> Locator:
        return self.page.get_by_test_id("total")

    def syrup_bottle(self) -> Locator:
        return self.page.get_by_role("img", name=re.compile(r"syrup bottle$"))

    def agree_and_pay(self) -> PaymentPage:
        self.page.get_by_role("button", name="Agree & pay").click()
        return PaymentPage(self.page, self.base_url)
