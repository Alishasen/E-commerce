from django import forms

from products.models import Payment


class CheckoutForm(forms.Form):

    # ------------------------------------------------------------
    # Contact information
    # ------------------------------------------------------------

    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your full name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
            }
        ),
    )

    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "98XXXXXXXX",
            }
        ),
    )

    # ------------------------------------------------------------
    # Shipping address
    # ------------------------------------------------------------

    shipping_address = forms.CharField(
        max_length=255,
        label="Delivery Address",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Street, area, landmark",
            }
        ),
    )

    shipping_city = forms.CharField(
        max_length=100,
        label="City",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "City",
            }
        ),
    )

    shipping_notes = forms.CharField(
        max_length=255,
        label="Delivery Notes (optional)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. call before arriving",
            }
        ),
    )

    # ------------------------------------------------------------
    # Payment method
    # ------------------------------------------------------------

    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label="Payment Method",
    )