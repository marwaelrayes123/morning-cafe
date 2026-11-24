from django.contrib import admin

from .models import Coffee, CoffeeVariant, MilkOption, Size


class CoffeeVariantInline(admin.TabularInline):
    model = CoffeeVariant
    fields = ("name", "slug", "price", "contains_milk", "is_iced", "sort_order", "is_available")
    extra = 0


@admin.register(Coffee)
class CoffeeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_iced", "sort_order", "is_available")
    list_editable = ("sort_order", "is_available")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CoffeeVariantInline]


@admin.register(CoffeeVariant)
class CoffeeVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "coffee", "price", "contains_milk", "is_available")
    list_filter = ("coffee", "contains_milk", "is_available")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MilkOption)
class MilkOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "color", "sort_order", "is_available")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "volume_ml", "price", "sort_order", "is_available")
    prepopulated_fields = {"slug": ("name",)}
