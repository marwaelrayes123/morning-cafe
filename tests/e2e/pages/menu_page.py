from .base_page import BasePage, starts_with


class MenuPage(BasePage):
    path = "/menu/"

    def coffee_names(self) -> list[str]:
        return self.page.locator(".menu-card-title").all_inner_texts()

    def choose(self, coffee: str):
        from .coffee_page import CoffeePage

        self.page.get_by_role("link", name=starts_with(coffee)).click()
        return CoffeePage(self.page, self.base_url)
