
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    # Add custom fields here if needed
    # For example:
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    class Meta:
        model = get_user_model()  # Use the custom User model defined in settings.py
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')  # Add custom fields here if needed



class DepositForm(forms.Form):
    stellar_public_key = forms.CharField(max_length=56)
    asset_code = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=20, decimal_places=6)

class WithdrawForm(forms.Form):
    stellar_public_key = forms.CharField(max_length=56)
    asset_code = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=20, decimal_places=6)

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=50, label='Username')

    
