from django.db import models

class StellarAccount(models.Model):
    public_key = models.CharField(max_length=56)
    secret_key = models.CharField(max_length=56)
    mnemonic = models.TextField()
    transaction_hash = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stellar_expert_link = models.URLField()
    federation_address = models.CharField(max_length=100)  # Add this field
    username = models.CharField(max_length=50)

    def __str__(self):
        return self.public_key



