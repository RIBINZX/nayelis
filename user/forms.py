from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import EmailInput, Textarea, TextInput
from user.models import Customer

from .models import Login


class LoginRegister(UserCreationForm):
    username = forms.CharField(label="username", widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = Login
        fields = ("username", "password1", "password2")


class UserRegistration(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("customer_name", "phone_number", "email", "address")
        widgets = {
            "customer_name": TextInput(
                attrs={
                    "class": "form-control",
                    "name": "customer_name",
                    "placeholder": "Full Name",
                    "required": "required",
                    "autocomplete": "off",
                }
            ),
            "phone_number": TextInput(
                attrs={
                    "class": "form-control",
                    "name": "phone_number",
                    "placeholder": "Phone Number",
                    "required": "required",
                    "autocomplete": "off",
                }
            ),
            "email": EmailInput(
                attrs={
                    "class": "form-control",
                    "name": "email",
                    "placeholder": "Email",
                    "required": "required",
                    "autocomplete": "off",
                }
            ),
            "address": Textarea(
                attrs={
                    "class": "form-control",
                    "name": "address",
                    "placeholder": "Full Address",
                    "required": "required",
                    "autocomplete": "off",
                }
            ),
            # 'username':Textarea(attrs={'class':'form-control','name':'username','placeholder':'username','required':'required','autocomplete':'off',}),
        }
