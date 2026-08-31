from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactMessage

        fields = [
            "name",
            "email",
            "message",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email",
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your message...",
                    "rows": 5,
                }
            ),

        }