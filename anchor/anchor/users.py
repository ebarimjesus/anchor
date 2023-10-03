# users.py

from zingypay.models import User, UserProfile, StellarAccount  # Import your models from your models.py file

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


