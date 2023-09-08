from django import forms

class DepositForm(forms.Form):
    stellar_public_key = forms.CharField(max_length=56)
    asset_code = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=20, decimal_places=6)

class WithdrawForm(forms.Form):
    stellar_public_key = forms.CharField(max_length=56)
    asset_code = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=20, decimal_places=6)


