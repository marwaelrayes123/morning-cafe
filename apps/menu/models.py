"""Menu data: coffee types, their sub-categories (variants), milk options and sizes.

`layers` describe how a drink looks in a glass, bottom to top, and are used to
draw the coffee pictures. Each layer is a dict:
    {"label": "Espresso", "color": "#4a2716", "ratio": 1, "kind": "coffee"}
`kind` "milk" layers are re-coloured with the milk the customer picks.
"""

from django.core.validators import MinValueValidator
from django.db import models

PRICE = {"max_digits": 6, "decimal_places": 2, "validators": [MinValueValidator(0)]}


class MenuItem(models.Model):
    """Fields shared by everything on the menu."""

    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Coffee(MenuItem):
    """A coffee type shown on the menu, e.g. Latte."""

    description = models.CharField(max_length=200, blank=True)
    layers = models.JSONField(default=list, blank=True)
    is_iced = models.BooleanField(default=False)

    class Meta(MenuItem.Meta):
        verbose_name_plural = "coffees"


class CoffeeVariant(MenuItem):
    """A sub-category of a coffee type, e.g. Caramel Latte. This is what gets ordered."""

    coffee = models.ForeignKey(Coffee, on_delete=models.CASCADE, related_name="variants")
    description = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(**PRICE)
    contains_milk = models.BooleanField(default=False)
    layers = models.JSONField(default=list, blank=True)
    is_iced = models.BooleanField(default=False)

    class Meta(MenuItem.Meta):
        verbose_name = "coffee variant"


class MilkOption(MenuItem):
    """A type of milk, e.g. Oat milk. `price` is added to the drink."""

    price = models.DecimalField(**PRICE, default=0)
    color = models.CharField(max_length=7, default="#fdf8ef", help_text="Hex colour used in the pictures")


class Size(MenuItem):
    """A cup size. `price` is added to the drink."""

    volume_ml = models.PositiveSmallIntegerField()
    price = models.DecimalField(**PRICE, default=0)
