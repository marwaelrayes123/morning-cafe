"""Starter menu. Used by `python manage.py seed_menu` and by the tests.

Running it again updates existing rows (matched by slug) instead of duplicating them.
Prices are in Danish kroner.
"""

from decimal import Decimal

from django.db import transaction

from .models import Coffee, CoffeeVariant, MilkOption, Size, Syrup

# --- Layer building blocks (what is in the cup, bottom to top) ---------------


def layer(label: str, color: str, ratio: float, kind: str = "coffee") -> dict:
    return {"label": label, "color": color, "ratio": ratio, "kind": kind}


ESPRESSO = layer("Espresso", "#4a2716", 1)
CREMA = layer("Crema", "#b5763e", 0.3)
WATER = layer("Hot water", "#7a4a2a", 3, "water")
MILK = layer("Steamed milk", "#fbf4e8", 2, "milk")
COLD_MILK = layer("Cold milk", "#fbf4e8", 2, "milk")
FOAM = layer("Milk foam", "#fffdf8", 1, "foam")
ICE = layer("Ice", "#e8f1f5", 1, "ice")
CHOCOLATE = layer("Chocolate", "#5b3320", 0.8)
WHITE_CHOCOLATE = layer("White chocolate", "#efe0c6", 0.8)
CREAM = layer("Whipped cream", "#fff8ee", 0.7, "cream")
CINNAMON = layer("Cinnamon", "#a0592b", 0.15, "topping")
COLD_BREW = layer("Cold brew", "#3b2012", 3)


def variant(name, description, price, *, milk=False, syrup=True, layers=()):
    return {
        "name": name,
        "description": description,
        "price": price,
        "contains_milk": milk,
        "allows_syrup": syrup,
        "layers": list(layers),
    }


# --- Menu ----------------------------------------------------------------------
# Each coffee type has one standard photo (static/web/img/coffee/<slug>.jpg) in its cup:
#   espresso cup: Espresso · americano cup: Americano
#   mug: Cappuccino, Flat White, Mocha · glass with handle: Latte, Iced Coffee

COFFEES = [
    {
        "name": "Espresso",
        "description": "Short, strong and intense. Served in a small espresso cup.",
        "variants": [
            variant(
                "Single Espresso",
                "One rich shot with golden crema.",
                "32",
                syrup=False,
                layers=[ESPRESSO, CREMA],
            ),
            variant(
                "Doppio",
                "A double shot for a double wake-up.",
                "38",
                syrup=False,
                layers=[ESPRESSO, ESPRESSO, CREMA],
            ),
            variant(
                "Ristretto",
                "A shorter, sweeter, more concentrated shot.",
                "34",
                syrup=False,
                layers=[ESPRESSO, CREMA],
            ),
            variant(
                "Macchiato",
                "Espresso marked with a spoon of milk foam.",
                "38",
                milk=True,
                syrup=False,
                layers=[ESPRESSO, FOAM],
            ),
        ],
    },
    {
        "name": "Americano",
        "description": "Espresso topped up with hot water. Smooth and long.",
        "variants": [
            variant("Classic Americano", "Espresso with hot water.", "38", layers=[ESPRESSO, WATER, CREMA]),
            variant(
                "Long Black",
                "Water first, espresso on top. Keeps the crema.",
                "40",
                layers=[WATER, ESPRESSO, CREMA],
            ),
            variant(
                "Americano with Milk",
                "A splash of milk to soften it.",
                "42",
                milk=True,
                layers=[ESPRESSO, WATER, MILK],
            ),
        ],
    },
    {
        "name": "Cappuccino",
        "description": "Equal parts espresso, steamed milk and silky foam.",
        "variants": [
            variant(
                "Classic Cappuccino", "The balanced classic.", "45", milk=True, layers=[ESPRESSO, MILK, FOAM]
            ),
            variant("Dry Cappuccino", "Less milk, more airy foam.", "45", milk=True, layers=[ESPRESSO, FOAM]),
            variant(
                "Cinnamon Cappuccino",
                "Dusted with warm cinnamon.",
                "48",
                milk=True,
                layers=[ESPRESSO, MILK, FOAM, CINNAMON],
            ),
        ],
    },
    {
        "name": "Latte",
        "description": "Espresso with lots of creamy steamed milk, served in a glass.",
        "variants": [
            variant(
                "Classic Latte", "Mellow, milky and smooth.", "48", milk=True, layers=[ESPRESSO, MILK, FOAM]
            ),
            variant(
                "Latte Macchiato",
                "Milk first, espresso poured through it in layers.",
                "50",
                milk=True,
                layers=[MILK, ESPRESSO, FOAM],
            ),
            variant(
                "Double Shot Latte",
                "Two shots for a stronger latte.",
                "54",
                milk=True,
                layers=[ESPRESSO, ESPRESSO, MILK, FOAM],
            ),
        ],
    },
    {
        "name": "Flat White",
        "description": "Strong espresso with a thin layer of velvety micro-foam.",
        "variants": [
            variant(
                "Classic Flat White",
                "Two shots and silky milk.",
                "48",
                milk=True,
                layers=[ESPRESSO, MILK, FOAM],
            ),
            variant(
                "Ristretto Flat White",
                "Made with sweeter ristretto shots.",
                "50",
                milk=True,
                layers=[ESPRESSO, CREMA, MILK, FOAM],
            ),
        ],
    },
    {
        "name": "Mocha",
        "description": "Espresso, chocolate and milk. Dessert in a mug.",
        "variants": [
            variant(
                "Classic Mocha",
                "Dark chocolate and whipped cream.",
                "52",
                milk=True,
                layers=[CHOCOLATE, ESPRESSO, MILK, CREAM],
            ),
            variant(
                "White Mocha",
                "Creamy white chocolate.",
                "55",
                milk=True,
                layers=[WHITE_CHOCOLATE, ESPRESSO, MILK, CREAM],
            ),
        ],
    },
    {
        "name": "Iced Coffee",
        "description": "Cold, refreshing and served over ice in a glass.",
        "is_iced": True,
        "variants": [
            variant(
                "Iced Latte",
                "Espresso poured over cold milk and ice.",
                "52",
                milk=True,
                layers=[ICE, COLD_MILK, ESPRESSO],
            ),
            variant(
                "Cold Brew", "Steeped for 18 hours. Smooth, never bitter.", "45", layers=[ICE, COLD_BREW]
            ),
            variant(
                "Iced Macchiato",
                "Cold milk and ice with a shot poured on top.",
                "52",
                milk=True,
                layers=[ICE, COLD_MILK, ESPRESSO],
            ),
        ],
    },
]

# Earlier versions of the menu had the syrup in the drink name. Syrup is now its own step.
RETIRED_VARIANTS = ["vanilla-latte", "caramel-latte", "hazelnut-latte", "iced-caramel-macchiato"]

MILKS = [
    # name, extra price (kr.), carton colour, plant-based
    ("Whole milk", "0", "#2f6db5", False),
    ("Semi-skimmed milk", "0", "#5aa0d8", False),
    ("Lactose-free milk", "3", "#7a5bb5", False),
    ("Soy milk", "5", "#5f8f3e", True),
    ("Oat milk", "6", "#c08b3e", True),
    ("Almond milk", "6", "#9a5f3c", True),
]

SYRUPS = [
    # name, extra price (kr.), bottle colour
    ("Vanilla", "5", "#e2b443"),
    ("Caramel", "5", "#b8641f"),
    ("Hazelnut", "5", "#7a4a2a"),
    ("Cinnamon", "5", "#a33b1c"),
    ("Lavender", "5", "#8e6cc0"),
]

SIZES = [
    # name, volume (ml), extra price (kr.)
    ("Small", 240, "0"),
    ("Medium", 360, "8"),
    ("Large", 480, "14"),
]

PHOTO_DIR = "web/img/coffee"


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


@transaction.atomic
def seed_menu() -> None:
    for coffee_order, data in enumerate(COFFEES):
        iced = data.get("is_iced", False)
        coffee, _ = Coffee.objects.update_or_create(
            slug=_slug(data["name"]),
            defaults={
                "name": data["name"],
                "description": data["description"],
                "layers": data["variants"][0]["layers"],
                "is_iced": iced,
                "image": f"{PHOTO_DIR}/{_slug(data['name'])}.jpg",
                "sort_order": coffee_order,
                "is_available": True,
            },
        )
        for variant_order, item in enumerate(data["variants"]):
            CoffeeVariant.objects.update_or_create(
                slug=_slug(item["name"]),
                defaults={
                    **item,
                    "coffee": coffee,
                    "price": Decimal(item["price"]),
                    "is_iced": iced,
                    "image": "",  # use the coffee type's standard cup photo
                    "sort_order": variant_order,
                    "is_available": True,
                },
            )

    CoffeeVariant.objects.filter(slug__in=RETIRED_VARIANTS).delete()

    for order, (name, price, color, plant_based) in enumerate(MILKS):
        MilkOption.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "price": Decimal(price),
                "color": color,
                "is_plant_based": plant_based,
                "sort_order": order,
            },
        )

    for order, (name, price, color) in enumerate(SYRUPS):
        Syrup.objects.update_or_create(
            slug=_slug(name),
            defaults={"name": name, "price": Decimal(price), "color": color, "sort_order": order},
        )

    for order, (name, volume, price) in enumerate(SIZES):
        Size.objects.update_or_create(
            slug=_slug(name),
            defaults={"name": name, "volume_ml": volume, "price": Decimal(price), "sort_order": order},
        )
