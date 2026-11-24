"""MenuService: read-only access to what is on the menu."""

from django.db.models import Min, Prefetch, Q, QuerySet

from .models import Coffee, CoffeeVariant, MilkOption, Size, Syrup


class MenuService:
    @staticmethod
    def coffees() -> QuerySet[Coffee]:
        """Available coffee types, each annotated with `from_price` (cheapest variant)."""
        available = Q(variants__is_available=True)
        return (
            Coffee.objects.filter(is_available=True)
            .annotate(from_price=Min("variants__price", filter=available))
            .filter(from_price__isnull=False)
        )

    @staticmethod
    def coffee_with_variants() -> QuerySet[Coffee]:
        """Coffees with their available variants prefetched as `available_variants`."""
        variants = CoffeeVariant.objects.filter(is_available=True)
        return Coffee.objects.filter(is_available=True).prefetch_related(
            Prefetch("variants", queryset=variants, to_attr="available_variants")
        )

    @staticmethod
    def variants() -> QuerySet[CoffeeVariant]:
        return CoffeeVariant.objects.filter(is_available=True, coffee__is_available=True).select_related(
            "coffee"
        )

    @staticmethod
    def milks() -> QuerySet[MilkOption]:
        return MilkOption.objects.filter(is_available=True)

    @staticmethod
    def syrups() -> QuerySet[Syrup]:
        return Syrup.objects.filter(is_available=True)

    @staticmethod
    def sizes() -> QuerySet[Size]:
        return Size.objects.filter(is_available=True)
