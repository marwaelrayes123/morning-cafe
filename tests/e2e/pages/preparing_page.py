from .base_page import BasePage
from .ready_page import ReadyPage


class PreparingPage(BasePage):
    """The "preparing your coffee" animation. It moves on by itself when the coffee is ready."""

    def wait_until_ready(self, timeout_ms: int = 15_000) -> ReadyPage:
        self.page.wait_for_url("**/ready/", timeout=timeout_ms)
        return ReadyPage(self.page, self.base_url)
