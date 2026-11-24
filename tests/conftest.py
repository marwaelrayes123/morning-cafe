import pytest

from apps.menu.seed import seed_menu


@pytest.fixture
def menu(db):
    """The starter menu, loaded into the test database."""
    seed_menu()


@pytest.fixture
def instant_prep(settings):
    """Coffee is ready immediately (no waiting in tests)."""
    settings.COFFEE_PREP_SECONDS = 0
