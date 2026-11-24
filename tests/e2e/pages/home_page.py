from .base_page import BasePage
from .menu_page import MenuPage


class HomePage(BasePage):
    path = "/"

    def welcome_text(self) -> str:
        return self.page.get_by_test_id("welcome-text").inner_text()

    def go_to_menu(self) -> MenuPage:
        self.page.get_by_role("link", name="See our menu").click()
        return MenuPage(self.page, self.base_url)
