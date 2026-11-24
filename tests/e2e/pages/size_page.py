from .base_page import BasePage, starts_with
from .review_page import ReviewPage


class SizePage(BasePage):
    path = "/order/size/"

    def choose(self, size: str) -> ReviewPage:
        self.page.get_by_role("button", name=starts_with(size)).click()
        return ReviewPage(self.page, self.base_url)
