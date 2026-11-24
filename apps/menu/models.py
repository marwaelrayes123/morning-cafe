"""Menu data: coffee types, their sub-categories (variants), milk options, syrups and sizes.

Prices are in the shop currency (settings.CAFE_CURRENCY, Danish kroner by default).
`image` is a path in the static folder. Each coffee type has one standard photo in its own
cup (espresso cup, americano cup, mug or glass); its variants use it unless they set their own.
`layers` list what is in the cup, bottom to top, and are shown as the ingredients:
    {"label": "Espresso", "color": "#4a2716", "ratio": 1, "kind": "coffee"}
"""

from django.core.validators import MinValueValidator
from django.db import models

PRICE = {"max_digits": 6, "decimal_places": 2, "validators": [MinValueValidator(0)]}

# Shown when a coffee has no photo of its own (path inside the static folder).
DEFAULT_PHOTO = "web/img/coffee/cappuccino.jpg"
PHOTO_HELP = "Static path, e.g. web/img/coffee/latte.jpg"


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
    image = models.CharField(max_length=120, blank=True, help_text=PHOTO_HELP)

    class Meta(MenuItem.Meta):
        verbose_name_plural = "coffees"

    @property
    def photo(self) -> str:
        return self.image or DEFAULT_PHOTO


class CoffeeVariant(MenuItem):
    """A sub-category of a coffee type, e.g. Caramel Latte. This is what gets ordered."""

    coffee = models.ForeignKey(Coffee, on_delete=models.CASCADE, related_name="variants")
    description = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(**PRICE)
    contains_milk = models.BooleanField(default=False)
    allows_syrup = models.BooleanField(default=True, help_text="Customers may add a syrup")
    layers = models.JSONField(default=list, blank=True)
    is_iced = models.BooleanField(default=False)
    image = models.CharField(max_length=120, blank=True, help_text=PHOTO_HELP)

    class Meta(MenuItem.Meta):
        verbose_name = "coffee variant"

    @property
    def photo(self) -> str:
        """Its own photo, else the coffee type's photo."""
        return self.image or self.coffee.photo

    @property
    def ingredients(self) -> list[str]:
        """What is in the cup, top to bottom, e.g. ["Milk foam", "Steamed milk", "Espresso"]."""
        return [layer["label"] for layer in reversed(self.layers)]


class MilkOption(MenuItem):
    """A type of milk, e.g. Oat milk. `price` is added to the drink."""

    price = models.DecimalField(**PRICE, default=0)
    color = models.CharField(max_length=7, default="#2f6db5", help_text="Hex colour of the carton band")
    is_plant_based = models.BooleanField(default=False)


class Syrup(MenuItem):
    """A flavour syrup, e.g. Vanilla. Shown as a bottle in `color` with the name on the label."""

    price = models.DecimalField(**PRICE, default=0)
    color = models.CharField(max_length=7, help_text="Hex colour of the syrup, e.g. #b8641f")


class Size(MenuItem):
    """A cup size. `price` is added to the drink."""

    volume_ml = models.PositiveSmallIntegerField()
    price = models.DecimalField(**PRICE, default=0)
