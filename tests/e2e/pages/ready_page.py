from .base_page import BasePage


class ReadyPage(BasePage):
    def order_number(self) -> str:
        return self.page.get_by_test_id("order-number").inner_text()
