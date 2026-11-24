import re

from playwright.sync_api import Locator, Page


def starts_with(text: str) -> re.Pattern:
    """Match an accessible name that begins with `text` (cards also contain a description)."""
    return re.compile("^" + re.escape(text))


class BasePage:
    """Shared behaviour for all page objects. No assertions in page objects."""

    path = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self):
        self.page.goto(self.base_url + self.path)
        return self

    def heading(self) -> Locator:
        return self.page.get_by_role("heading", level=1)

    def _next_order_step(self):
        """After a choice, the shop skips steps that don't apply (e.g. no milk for an espresso).
        Return the page object for wherever we landed."""
        from .milk_page import MilkPage
        from .review_page import ReviewPage
        from .size_page import SizePage
        from .syrup_page import SyrupPage

        self.page.wait_for_load_state()
        for suffix, page_class in (
            ("/order/milk/", MilkPage),
            ("/order/syrup/", SyrupPage),
            ("/order/size/", SizePage),
            ("/order/review/", ReviewPage),
        ):
            if self.page.url.endswith(suffix):
                return page_class(self.page, self.base_url)
        raise AssertionError(f"Unexpected page after choosing: {self.page.url}")
