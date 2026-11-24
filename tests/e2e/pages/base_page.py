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
