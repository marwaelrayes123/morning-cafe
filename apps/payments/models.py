from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    """One payment attempt. Only the last 4 digits of the card are kept."""

    class Status(models.TextChoices):
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    status = models.CharField(max_length=10, choices=Status.choices)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    card_last4 = models.CharField(max_length=4)
    reference = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.reference} · {self.get_status_display()}"
