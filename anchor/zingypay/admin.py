from django.contrib import admin

# Register your models here.

from .models import User, StellarAccount, Transaction, UserProfile

# Define admin classes for your models

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

class StellarAccountAdmin(admin.ModelAdmin):
    list_display = ('public_key', 'balance', 'stellar_expert_link', 'federation_address', 'username')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stellar_public_key', 'asset_code', 'amount', 'transaction_hash', 'timestamp')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stellar_public_key', 'stellar_secret_key', 'mnemonic')

# Register your models with their respective admin classes

admin.site.register(User, UserAdmin)
admin.site.register(StellarAccount, StellarAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)


