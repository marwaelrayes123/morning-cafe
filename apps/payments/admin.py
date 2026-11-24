from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "order", "status", "amount", "card_last4", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "order__number")
