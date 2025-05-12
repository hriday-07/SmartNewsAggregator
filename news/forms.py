from django import forms
from django.contrib.auth.models import User
from .models import Category
from django.contrib.auth.forms import AuthenticationForm


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }
        labels = {
            "username": "Username",
            "email": "Email",
        }
        help_texts = {
            "username": "Enter a unique username.",
            "email": "Enter a valid email address.",
        }
        error_messages = {
            "username": {
                "required": "Username is required.",
                "unique": "This username is already taken.",
            },
            "email": {
                "required": "Email is required.",
                "invalid": "Enter a valid email address.",
            },
        }
        field_classes = {
            "username": forms.CharField,
            "email": forms.EmailField,
        }


class CategorySelectionForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )


class SearchForm(forms.Form):
    query = forms.CharField(label="Search articles", max_length=300)
