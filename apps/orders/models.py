"""A placed order. Names and prices are copied in, so later menu changes never rewrite old orders."""

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.menu.models import DEFAULT_PHOTO, CoffeeVariant


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Waiting for payment"
        PAID = "paid", "Paid"
        FAILED = "failed", "Payment failed"

    number = models.CharField(max_length=12, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    customer_name = models.CharField(max_length=60, blank=True)

    variant = models.ForeignKey(CoffeeVariant, on_delete=models.SET_NULL, null=True, related_name="orders")
    coffee_name = models.CharField(max_length=60)
    variant_name = models.CharField(max_length=60)
    milk_name = models.CharField(max_length=60, blank=True)
    syrup_name = models.CharField(max_length=60, blank=True)
    size_name = models.CharField(max_length=30)

    variant_price = models.DecimalField(max_digits=6, decimal_places=2)
    milk_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    syrup_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    size_price = models.DecimalField(max_digits=6, decimal_places=2)
    total = models.DecimalField(max_digits=7, decimal_places=2)

    # How the drink looks: {"image": "web/img/coffee/...jpg", "syrup_color": "#..." or None}
    picture = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.number} · {self.variant_name}"

    @property
    def photo(self) -> str:
        return self.picture.get("image") or DEFAULT_PHOTO

    @property
    def syrup_color(self) -> str | None:
        return self.picture.get("syrup_color")

    @property
    def is_paid(self) -> bool:
        return self.status == self.Status.PAID

    @property
    def ready_at(self) -> datetime | None:
        if self.paid_at is None:
            return None
        return self.paid_at + timedelta(seconds=settings.COFFEE_PREP_SECONDS)

    def is_ready(self, now: datetime | None = None) -> bool:
        return self.ready_at is not None and (now or timezone.now()) >= self.ready_at

    def seconds_until_ready(self, now: datetime | None = None) -> int:
        if self.ready_at is None:
            return settings.COFFEE_PREP_SECONDS
        remaining = (self.ready_at - (now or timezone.now())).total_seconds()
        return max(0, round(remaining))

    @property
    def price_lines(self) -> list[tuple[str, object]]:
        lines = [(self.variant_name, self.variant_price)]
        if self.milk_name:
            lines.append((self.milk_name, self.milk_price))
        if self.syrup_name:
            lines.append((f"{self.syrup_name} syrup", self.syrup_price))
        lines.append((f"Size: {self.size_name}", self.size_price))
        return lines
