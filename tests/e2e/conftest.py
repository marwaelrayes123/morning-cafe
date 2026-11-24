import os

import pytest

from apps.menu.seed import seed_menu
from tests.e2e.pages.home_page import HomePage

# Playwright's sync API runs an event loop in the test thread, which makes Django
# think DB calls happen in async code. Safe to allow in tests only.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def seeded_menu(transactional_db):
    """Every browser test starts with the starter menu."""
    seed_menu()


@pytest.fixture(autouse=True)
def quick_prep(settings):
    """Keep the "preparing" animation short in browser tests."""
    settings.COFFEE_PREP_SECONDS = 2


@pytest.fixture
def home_page(page, live_server):
    return HomePage(page, live_server.url)
