from django import forms
from us import states  # https://pypi.org/project/us/

state_list = sorted(
    status.mapping("abbr", "name").items(),
    key=lambda x: x[1]
)

class ContactForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

class AddressForm(forms.Form):
    address_1 = forms.CharField()
    address_2 = forms.CharField()
    city = forms.CharField()
    state = forms.ChoiceField(choices=state_list)
    zip_code = forms.CharField()

class BankAccount(forms.Form):
    account_number = forms.CharField()
    routing_number = forms.CharField()


    