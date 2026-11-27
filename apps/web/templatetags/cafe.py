"""Template helpers: prices and syrup bottles.

Usage:
    {% load cafe %}
    {{ variant.price|money }}        -> "52 kr."   (DKK)
    {{ variant.price|money:"+" }}    -> "+ 6 kr."
    {% syrup_bottle syrup.name syrup.color %}
    {% milk_carton milk.name milk.color milk.is_plant_based %}
"""

import secrets
from decimal import Decimal

from django import template
from django.conf import settings

register = template.Library()


def format_money(value: Decimal, currency: str) -> str:
    """Danish kroner the Danish way ("52 kr.", "52,50 kr."); other currencies as "€3.90"."""
    value = Decimal(value)
    if currency == "DKK":
        # Whole kroner without decimals ("52 kr."), otherwise with øre ("52,50 kr.").
        amount = f"{value:,.0f}" if value == value.to_integral_value() else f"{value:,.2f}"
        # Danish style: "." for thousands and "," for decimals.
        amount = amount.replace(",", "§").replace(".", ",").replace("§", ".")
        return f"{amount} kr."
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    return f"{symbols.get(currency, currency + ' ')}{value:,.2f}"


@register.filter
def money(value, sign: str = "") -> str:
    if value in (None, ""):
        return ""
    text = format_money(value, settings.CAFE_CURRENCY)
    return f"{sign} {text}" if sign else text


def _shade(hex_color: str, factor: float) -> str:
    """Darken (factor < 1) or lighten (factor > 1) a "#rrggbb" colour."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    if factor < 1:
        r, g, b = (round(c * factor) for c in (r, g, b))
    else:
        r, g, b = (round(c + (255 - c) * (factor - 1)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


@register.inclusion_tag("web/partials/syrup_bottle.html")
def syrup_bottle(name: str, color: str, css_class: str = ""):
    """A syrup bottle filled with `color`, with `name` on the label."""
    label = name.upper()
    return {
        "uid": "bottle-" + secrets.token_hex(4),
        "name": name,
        "label": label,
        # Long names are squeezed to fit the label.
        "label_length": min(38, round(len(label) * 5.8)),
        "color": color,
        "dark": _shade(color, 0.62),
        "light": _shade(color, 1.35),
        "css_class": css_class,
    }


@register.inclusion_tag("web/partials/milk_carton.html")
def milk_carton(name: str, color: str, plant_based: bool = False, css_class: str = ""):
    """A milk carton with a band in `color` and the milk's name, e.g. "OAT" for "Oat milk"."""
    label = name.removesuffix(" milk").removesuffix(" Milk").upper()
    return {
        "uid": "carton-" + secrets.token_hex(4),
        "name": name,
        "label": label,
        "label_length": min(40, round(len(label) * 6.2)),
        "color": color,
        "dark": _shade(color, 0.7),
        "plant_based": plant_based,
        "css_class": css_class,
    }
