import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def test_home_shows_welcome_message(home_page):
    home_page.open()

    expect(home_page.heading()).to_have_text("Welcome to Morning Cafe")
    assert "Build your perfect coffee" in home_page.welcome_text()


def test_see_our_menu_opens_the_menu(home_page):
    menu = home_page.open().go_to_menu()

    expect(menu.page).to_have_url(re.compile(r"/menu/$"))
    expect(menu.heading()).to_have_text("Our menu")
