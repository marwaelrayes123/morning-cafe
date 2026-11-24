"""Starter menu. Used by `python manage.py seed_menu` and by the tests.

Running it again updates existing rows (matched by slug) instead of duplicating them.
"""

from decimal import Decimal

from django.db import transaction

from .models import Coffee, CoffeeVariant, MilkOption, Size

# --- Layer building blocks (bottom to top in the glass) ----------------------


def layer(label: str, color: str, ratio: float, kind: str = "coffee") -> dict:
    return {"label": label, "color": color, "ratio": ratio, "kind": kind}


ESPRESSO = "#4a2716"
CREMA = "#b5763e"
WATER = "#7a4a2a"
MILK = "#fbf4e8"
FOAM = "#fffdf8"


def espresso(r=1.0):
    return layer("Espresso", ESPRESSO, r)


def crema(r=0.3):
    return layer("Crema", CREMA, r)


def milk(r=1.0):
    return layer("Steamed milk", MILK, r, "milk")


def foam(r=1.0):
    return layer("Milk foam", FOAM, r, "foam")


def syrup(label, color, r=0.4):
    return layer(label, color, r, "syrup")


# --- Menu ----------------------------------------------------------------------

COFFEES = [
    {
        "name": "Espresso",
        "description": "Short, strong and intense. The heart of every coffee.",
        "variants": [
            ("Single Espresso", "One rich shot with golden crema.", "2.20", False, [espresso(2), crema(0.4)]),
            ("Doppio", "A double shot for a double wake-up.", "2.80", False, [espresso(3), crema(0.5)]),
            (
                "Ristretto",
                "A shorter, sweeter, more concentrated shot.",
                "2.40",
                False,
                [espresso(1.4), crema(0.4)],
            ),
            ("Macchiato", "Espresso marked with a spoon of milk foam.", "2.90", True, [espresso(2), foam(1)]),
        ],
    },
    {
        "name": "Americano",
        "description": "Espresso topped up with hot water. Smooth and long.",
        "variants": [
            (
                "Classic Americano",
                "Espresso with hot water.",
                "2.80",
                False,
                [espresso(1.5), layer("Hot water", WATER, 3, "water"), crema(0.3)],
            ),
            (
                "Long Black",
                "Water first, espresso on top. Keeps the crema.",
                "2.90",
                False,
                [layer("Hot water", WATER, 2.5, "water"), espresso(1.6), crema(0.4)],
            ),
            (
                "Americano with Milk",
                "A splash of milk to soften it.",
                "3.10",
                True,
                [espresso(1.5), layer("Hot water", WATER, 2.5, "water"), milk(1)],
            ),
        ],
    },
    {
        "name": "Cappuccino",
        "description": "Equal parts espresso, steamed milk and silky foam.",
        "variants": [
            ("Classic Cappuccino", "The balanced classic.", "3.40", True, [espresso(1), milk(1), foam(1.2)]),
            (
                "Dry Cappuccino",
                "Less milk, more airy foam.",
                "3.40",
                True,
                [espresso(1), milk(0.5), foam(1.8)],
            ),
            (
                "Cinnamon Cappuccino",
                "Dusted with warm cinnamon.",
                "3.70",
                True,
                [espresso(1), milk(1), foam(1.1), layer("Cinnamon", "#a0592b", 0.15, "topping")],
            ),
        ],
    },
    {
        "name": "Latte",
        "description": "Espresso with lots of creamy steamed milk.",
        "variants": [
            ("Classic Latte", "Mellow, milky and smooth.", "3.60", True, [espresso(1), milk(3), foam(0.5)]),
            (
                "Vanilla Latte",
                "With sweet vanilla syrup.",
                "3.90",
                True,
                [syrup("Vanilla syrup", "#f1d98f"), espresso(1), milk(2.6), foam(0.5)],
            ),
            (
                "Caramel Latte",
                "With buttery caramel syrup.",
                "3.90",
                True,
                [syrup("Caramel syrup", "#c98a3c"), espresso(1), milk(2.6), foam(0.5)],
            ),
            (
                "Hazelnut Latte",
                "With toasty hazelnut syrup.",
                "3.90",
                True,
                [syrup("Hazelnut syrup", "#9c6a3a"), espresso(1), milk(2.6), foam(0.5)],
            ),
        ],
    },
    {
        "name": "Flat White",
        "description": "Strong espresso with a thin layer of velvety micro-foam.",
        "variants": [
            (
                "Classic Flat White",
                "Two shots and silky milk.",
                "3.50",
                True,
                [espresso(1.4), milk(1.6), foam(0.25)],
            ),
            (
                "Ristretto Flat White",
                "Made with sweeter ristretto shots.",
                "3.70",
                True,
                [espresso(1.2), crema(0.2), milk(1.6), foam(0.25)],
            ),
        ],
    },
    {
        "name": "Mocha",
        "description": "Espresso, chocolate and milk. Dessert in a cup.",
        "variants": [
            (
                "Classic Mocha",
                "Dark chocolate and whipped cream.",
                "4.00",
                True,
                [
                    layer("Chocolate", "#5b3320", 0.8),
                    espresso(1),
                    milk(1.6),
                    layer("Whipped cream", "#fff8ee", 0.7, "cream"),
                ],
            ),
            (
                "White Mocha",
                "Creamy white chocolate.",
                "4.20",
                True,
                [
                    layer("White chocolate", "#efe0c6", 0.8),
                    espresso(1),
                    milk(1.6),
                    layer("Whipped cream", "#fff8ee", 0.7, "cream"),
                ],
            ),
        ],
    },
    {
        "name": "Iced Coffee",
        "description": "Cold, refreshing and served over ice.",
        "is_iced": True,
        "variants": [
            ("Iced Latte", "Espresso poured over cold milk and ice.", "3.90", True, [milk(2.5), espresso(1)]),
            (
                "Cold Brew",
                "Steeped for 18 hours. Smooth, never bitter.",
                "3.60",
                False,
                [layer("Cold brew", "#3b2012", 3.4)],
            ),
            (
                "Iced Caramel Macchiato",
                "Caramel, cold milk and a shot on top.",
                "4.30",
                True,
                [
                    syrup("Caramel syrup", "#c98a3c"),
                    milk(2.4),
                    espresso(1),
                    layer("Caramel drizzle", "#b06f2a", 0.15, "topping"),
                ],
            ),
        ],
    },
]

MILKS = [
    ("Whole milk", "0.00", "#fdf8ef"),
    ("Semi-skimmed milk", "0.00", "#fbf9f4"),
    ("Lactose-free milk", "0.30", "#fffaf0"),
    ("Soy milk", "0.40", "#f5ecd6"),
    ("Oat milk", "0.50", "#efe0c4"),
    ("Almond milk", "0.50", "#f1e2cc"),
]

SIZES = [
    ("Small", 240, "0.00"),
    ("Medium", 360, "0.60"),
    ("Large", 480, "1.10"),
]


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


@transaction.atomic
def seed_menu() -> None:
    for coffee_order, data in enumerate(COFFEES):
        iced = data.get("is_iced", False)
        first_layers = data["variants"][0][4]
        coffee, _ = Coffee.objects.update_or_create(
            slug=_slug(data["name"]),
            defaults={
                "name": data["name"],
                "description": data["description"],
                "layers": first_layers,
                "is_iced": iced,
                "sort_order": coffee_order,
                "is_available": True,
            },
        )
        for variant_order, (name, description, price, has_milk, layers) in enumerate(data["variants"]):
            CoffeeVariant.objects.update_or_create(
                slug=_slug(name),
                defaults={
                    "coffee": coffee,
                    "name": name,
                    "description": description,
                    "price": Decimal(price),
                    "contains_milk": has_milk,
                    "layers": layers,
                    "is_iced": iced,
                    "sort_order": variant_order,
                    "is_available": True,
                },
            )

    for order, (name, price, color) in enumerate(MILKS):
        MilkOption.objects.update_or_create(
            slug=_slug(name),
            defaults={"name": name, "price": Decimal(price), "color": color, "sort_order": order},
        )

    for order, (name, volume, price) in enumerate(SIZES):
        Size.objects.update_or_create(
            slug=_slug(name),
            defaults={"name": name, "volume_ml": volume, "price": Decimal(price), "sort_order": order},
        )
