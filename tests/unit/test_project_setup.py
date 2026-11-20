"""Smoke tests: the project is wired up correctly."""

from decimal import Decimal

from django.apps import apps
from django.conf import settings


def test_local_apps_are_installed():
    for label in ("menu", "orders", "payments", "web"):
        assert apps.is_installed(f"apps.{label}")


def test_rest_framework_is_installed():
    assert apps.is_installed("rest_framework")


def test_business_settings_have_safe_types():
    assert isinstance(settings.TAKEAWAY_CUP_FEE, Decimal)
    assert settings.MAX_FLAVOURS_PER_DRINK == 3
    assert settings.MAX_QUANTITY_PER_ORDER == 10


def test_secret_key_is_not_the_old_hardcoded_one():
    assert not settings.SECRET_KEY.startswith("django-insecure-qf3")
