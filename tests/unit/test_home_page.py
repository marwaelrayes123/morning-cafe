"""Home (welcome) page renders and links to the menu."""

import pytest
from django.urls import reverse


def test_home_page_shows_welcome(client):
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert "web/home.html" in [t.name for t in response.templates]
    assert "Welcome to Morning Cafe" in response.content.decode()


def test_home_page_links_to_menu(client):
    html = client.get(reverse("web:home")).content.decode()

    assert f'href="{reverse("web:menu")}"' in html
    assert "See our menu" in html


@pytest.mark.django_db
def test_menu_page_is_reachable(client):
    response = client.get(reverse("web:menu"))

    assert response.status_code == 200
    assert "Our menu" in response.content.decode()
