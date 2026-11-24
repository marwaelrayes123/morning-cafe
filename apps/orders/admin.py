from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "variant_name",
        "milk_name",
        "syrup_name",
        "size_name",
        "total",
        "status",
        "customer_name",
        "created_at",
    )
    list_filter = ("status", "coffee_name")
    search_fields = ("number", "customer_name")
    readonly_fields = ("created_at", "paid_at")
