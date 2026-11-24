import re
from datetime import date

from django import forms

from apps.payments.validators import luhn_valid, normalize_card_number


class PaymentForm(forms.Form):
    """Fake card form. The full card number is validated, then only passed to the gateway."""

    customer_name = forms.CharField(
        label="Your name",
        max_length=60,
        widget=forms.TextInput(attrs={"autocomplete": "given-name", "placeholder": "Sara"}),
    )
    card_number = forms.CharField(
        label="Card number",
        max_length=23,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "4242 4242 4242 4242"}),
    )
    expiry = forms.CharField(
        label="Expiry (MM/YY)",
        max_length=5,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "12/30"}),
    )
    cvc = forms.CharField(
        label="CVC",
        max_length=4,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "123"}),
    )

    def clean_customer_name(self) -> str:
        name = self.cleaned_data["customer_name"].strip()
        if not name:
            raise forms.ValidationError("Please tell us your name so we can call you.")
        return name

    def clean_card_number(self) -> str:
        number = normalize_card_number(self.cleaned_data["card_number"])
        if not luhn_valid(number):
            raise forms.ValidationError("This card number is not valid.")
        return number

    def clean_expiry(self) -> str:
        value = self.cleaned_data["expiry"].strip()
        match = re.fullmatch(r"(0[1-9]|1[0-2])/(\d{2})", value)
        if not match:
            raise forms.ValidationError("Use the format MM/YY, e.g. 12/30.")
        month, year = int(match[1]), 2000 + int(match[2])
        today = date.today()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError("This card has expired.")
        return value

    def clean_cvc(self) -> str:
        value = self.cleaned_data["cvc"].strip()
        if not re.fullmatch(r"\d{3,4}", value):
            raise forms.ValidationError("The CVC is the 3 or 4 digits on the back of the card.")
        return value
