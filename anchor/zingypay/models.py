# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
import decimal

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, default='')

    class Meta:
        permissions = [
            ("can_view_special_content", "Can view special content"),
        ]
        abstract = False

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    federation_address = models.CharField(max_length=100, default='')
    stellar_public_key = models.CharField(max_length=56, default='')
    stellar_secret_key = models.CharField(max_length=56, default='') 
    mnemonic = models.TextField(default='')

    def __str__(self):
        return self.user.username

class StellarAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    public_key = models.CharField(max_length=56, default='')
    secret_key = models.CharField(max_length=56, default='')
    mnemonic = models.CharField(max_length=100, default='')
    transaction_hash = models.CharField(max_length=64, default='')
    balance = models.DecimalField(max_digits=20, decimal_places=7, default='')
    stellar_expert_link = models.URLField(max_length=200, default='')
    username = models.CharField(max_length=50, default='')
    federation_address = models.CharField(max_length=100, default='')
    home_domain = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"Username: {self.username}, Public Key: {self.public_key}, Secret Key: {self.secret_key}, Mnemonic: {self.mnemonic}, Federation Address: {self.federation_address}, Home Domain: {self.home_domain}, Balance: {self.balance}"


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True, default='')
    name = models.CharField(max_length=50, default='')
    symbol = models.CharField(max_length=10, default='')

    def __str__(self):
        return self.code

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stellar_public_key = models.CharField(max_length=56, default='')
    asset_code = models.CharField(max_length=12, default='')
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=decimal.Decimal('0.00'))
    transaction_hash = models.CharField(max_length=64, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='')
    transaction_type = models.CharField(max_length=50, default='')

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_ngn = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    amount_oso = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    amount_afro = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    payment_reference = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} - NGN: {self.amount_ngn}, OSO: {self.amount_oso}, AFRO: {self.amount_afro}"

class TokenConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_oso = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    amount_afro = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OSO to AFRO Conversion by {self.user.username}: OSO: {self.amount_oso}, AFRO: {self.amount_afro}"


