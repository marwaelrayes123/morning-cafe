from .base_page import BasePage, starts_with
from .size_page import SizePage


class SyrupPage(BasePage):
    """Syrup bottles in their own colour with the name on the label."""

    path = "/order/syrup/"

    def syrup_names(self) -> list[str]:
        return self.page.locator(".shelf-card:not(.shelf-card--none) .option-title").all_inner_texts()

    def choose(self, syrup: str) -> SizePage:
        self.page.get_by_role("button", name=starts_with(syrup)).click()
        return SizePage(self.page, self.base_url)

    def no_syrup(self) -> SizePage:
        self.page.get_by_role("button", name=starts_with("No syrup")).click()
        return SizePage(self.page, self.base_url)
