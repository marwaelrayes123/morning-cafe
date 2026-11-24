from playwright.sync_api import Locator

from .base_page import BasePage
from .preparing_page import PreparingPage


class PaymentPage(BasePage):
    def fill(self, name: str, card: str, expiry: str, cvc: str) -> None:
        self.page.get_by_label("Your name").fill(name)
        self.page.get_by_label("Card number").fill(card)
        self.page.get_by_label("Expiry (MM/YY)").fill(expiry)
        self.page.get_by_label("CVC").fill(cvc)
        self.page.get_by_role("button", name="Pay").click()

    def pay(self, name: str, card: str, expiry: str, cvc: str) -> PreparingPage:
        self.fill(name, card, expiry, cvc)
        return PreparingPage(self.page, self.base_url)

    def error_message(self) -> Locator:
        return self.page.get_by_role("alert")
