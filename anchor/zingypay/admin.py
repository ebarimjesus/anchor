from django.contrib import admin
from .models import User, StellarAccount, Transaction, UserProfile, Currency, Payment, TokenConversion, Balance, PaymentTransaction

# Define admin classes for your models

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

class StellarAccountAdmin(admin.ModelAdmin):
    list_display = ('public_key', 'balance', 'stellar_expert_link', 'federation_address', 'username')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stellar_public_key', 'asset_code', 'amount', 'transaction_hash', 'timestamp')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stellar_public_key', 'stellar_secret_key', 'mnemonic')

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'currency', 'balance')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_ngn', 'amount_oso', 'amount_afro', 'payment_reference', 'timestamp')

class TokenConversionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_oso', 'amount_afro', 'timestamp')

class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('user',  'timestamp')

# Register your models with their respective admin classes

admin.site.register(User, UserAdmin)
admin.site.register(StellarAccount, StellarAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(TokenConversion, TokenConversionAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)


