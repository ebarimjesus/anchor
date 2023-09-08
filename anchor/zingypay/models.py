from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

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
    public_key = models.CharField(max_length=56, default='')
    secret_key = models.CharField(max_length=56, default='')
    mnemonic = models.TextField(default='')
    transaction_hash = models.CharField(max_length=64, default='')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stellar_expert_link = models.URLField(default='')
    federation_address = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.public_key

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
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    transaction_hash = models.CharField(max_length=64, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default='')
    transaction_type = models.CharField(max_length=50, default='')

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"


