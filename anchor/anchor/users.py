# users.py
from django.db import models
from zingypay.models import User, UserProfile, StellarAccount, BankAccount  # Import your models from your models.py file

def user_for_account(stellar_account):
    try:
        # Assuming stellar_account is the public key
        return StellarAccount.objects.get(public_key=stellar_account).user
    except StellarAccount.DoesNotExist:
        return None

def create_user(form_data):
    user = User.objects.create(
        username=form_data.cleaned_data['username'],
        email=form_data.cleaned_data['email'],
        # Additional fields as per your User model
    )
    # Create UserProfile for the user
    UserProfile.objects.create(user=user)
    return user

def update_user_address(form_data):
    user = User.objects.get(username=form_data.cleaned_data['username'])
    # Assuming you have an 'address' field in your UserProfile model
    user_profile = UserProfile.objects.get(user=user)
    user_profile.address = form_data.cleaned_data['address']
    user_profile.save()

def fields_for_type(user_type):
    """
    Define fields based on user type.

    Args:
        user_type (str): Type of user (e.g., 'admin', 'regular').

    Returns:
        dict: A dictionary where keys are field names and values are default values for these fields.
    """
    if user_type == 'admin':
        return {
            'field1': 'default_value1',
            'field2': 'default_value2',
            # Add more fields as needed
        }
    elif user_type == 'regular':
        return {
            'fieldA': 'default_valueA',
            'fieldB': 'default_valueB',
            # Add more fields as needed
        }
    else:
        # Default fields for unknown user types
        return {
            'default_field': 'default_value',
        }

def user_for_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    routing_number = models.CharField(max_length=20)
    # Add other fields as needed

    def __str__(self):
        return f"Bank Account for {self.user.username}"




