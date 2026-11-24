"""Template helpers: `{% coffee_cup %}` draws a drink as a glass with its layers; `|money` formats prices.

Usage:
    {% load cafe %}
    {% coffee_cup variant.layers iced=variant.is_iced milk_color=milk.color %}
    {{ variant.price|money }}
"""

import secrets
from decimal import Decimal

from django import template
from django.conf import settings

register = template.Library()

CURRENCY_SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£", "DKK": "kr "}

# Inside of the glass in SVG units (viewBox 0 0 160 170).
FILL_TOP = 42
FILL_BOTTOM = 150


@register.filter
def money(value) -> str:
    """Decimal("3.9") -> "€3.90"."""
    if value in (None, ""):
        return ""
    symbol = CURRENCY_SYMBOLS.get(settings.CAFE_CURRENCY, settings.CAFE_CURRENCY + " ")
    return f"{symbol}{Decimal(value):.2f}"


@register.inclusion_tag("web/partials/cup.html")
def coffee_cup(layers, iced=False, milk_color=None, label="", css_class="", legend=False, decorative=False):
    """Draw a cup. `layers` go bottom to top; their `ratio` decides how tall each one is.

    Use `decorative=True` inside links/buttons whose text already names the drink, so screen
    readers do not read the picture twice.
    """
    layers = layers or []
    total_ratio = sum(float(layer.get("ratio", 1)) for layer in layers) or 1
    fill_height = FILL_BOTTOM - FILL_TOP

    shapes = []
    y = FILL_BOTTOM
    for layer in layers:
        height = fill_height * float(layer.get("ratio", 1)) / total_ratio
        y -= height
        color = layer.get("color", "#4a2716")
        if milk_color and layer.get("kind") == "milk":
            color = milk_color
        # +0.6 overlap hides hairline gaps between layers when the SVG is scaled.
        shapes.append({**layer, "y": round(y, 1), "height": round(height + 0.6, 1), "color": color})

    return {
        "uid": "cup-" + secrets.token_hex(4),
        "shapes": shapes,
        "legend_items": list(reversed(shapes)),  # top layer first, like reading the glass
        "iced": iced,
        "label": label or "A cup of coffee",
        "css_class": css_class,
        "legend": legend,
        "decorative": decorative,
    }
