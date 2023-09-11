
from django.shortcuts import render, redirect
from django.http import HttpResponse
from stellar_sdk import Server, Keypair, TransactionBuilder, Asset
import requests
import json
import re
from .models import Transaction, UserProfile, User, StellarAccount, Payment, TokenConversion, Balance, Currency
from .forms import DepositForm
from .forms import UsernameForm
import paystackapi  # Make sure you've installed this package


import os
import requests
import toml
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages



from django.core.exceptions import ObjectDoesNotExist
import datetime
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from stellar_sdk.asset import Asset
from stellar_sdk.keypair import Keypair
from stellar_sdk.network import Network
from stellar_sdk.server import Server
from stellar_sdk.transaction_builder import TransactionBuilder
from stellar_sdk.operation import Payment
from stellar_sdk.exceptions import NotFoundError, BadResponseError, BadRequestError, ConnectionError


import hashlib
import hmac

import struct

from typing import Union
from enum import Enum, unique

from mnemonic import Mnemonic
from mnemonic.mnemonic import PBKDF2_ROUNDS


from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import RegistrationForm
from .models import Transaction, UserProfile, User, Currency

import requests
import json
import re



class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Create this template
    # Additional customization if needed

class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html' 
    # Additional customization if needed

class RegistrationView(View):
    template_name = 'registration/register.html'  # Create this template
    form_class = RegistrationForm  # Use the custom registration form
    success_url = reverse_lazy('login')  # URL to redirect after successful registration

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            # Additional logic like sending confirmation email, logging in the user, etc.
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})



def home(request):
    return render(request, 'index.html')


# Stellar server instance
server = Server(horizon_url="https://horizon.stellar.org") 




# Generate a new key pair
keypair = Keypair.random()






@unique
class Language(Enum):
    """The type of language supported by the mnemonic."""

    JAPANESE = "japanese"
    FRENCH = "french"
    ENGLISH = "english"
    SPANISH = "spanish"
    ITALIAN = "italian"
    KOREAN = "korean"
    CHINESE_SIMPLIFIED = "chinese_simplified"
    CHINESE_TRADITIONAL = "chinese_traditional"




class StellarMnemonic(Mnemonic):
    """Please use :func:`stellar_sdk.keypair.Keypair.generate_mnemonic_phrase`
    and :func:`stellar_sdk.keypair.Keypair.from_mnemonic_phrase`
    """

    STELLAR_ACCOUNT_PATH_FORMAT = "m/44'/148'/%d'"
    FIRST_HARDENED_INDEX = 0x80000000
    SEED_MODIFIER = b"ed25519 seed"

    def __init__(self, language: Union[str, Language] = Language.ENGLISH) -> None:
        if isinstance(language, Language):
            language = language.value
        else:
            if language not in set(item.value for item in Language):
                raise ValueError("This language is not supported.")

        super().__init__(language)

    def to_seed(self, mnemonic: str, passphrase: str = "", index: int = 0) -> bytes:  # type: ignore[override]
        if not self.check(mnemonic):
            raise ValueError(
                "Invalid mnemonic, please check if the mnemonic is correct, "
                "or if the language is set correctly."
            )
        mnemonic = self.normalize_string(mnemonic)
        passphrase = self.normalize_string(passphrase)
        passphrase = "mnemonic" + passphrase
        mnemonic_bytes = mnemonic.encode("utf-8")
        passphrase_bytes = passphrase.encode("utf-8")
        stretched = hashlib.pbkdf2_hmac(
            "sha512", mnemonic_bytes, passphrase_bytes, PBKDF2_ROUNDS
        )
        return self.derive(stretched[:64], index)

    def generate(self, strength: int = 128) -> str:
        if strength not in (128, 160, 192, 224, 256):
            raise ValueError(
                f"Strength should be one of the following (128, 160, 192, 224, 256), but it is not ({strength})."
            )
        return self.to_mnemonic(os.urandom(strength // 8))

    @staticmethod
    def derive(seed: bytes, index: int) -> bytes:
        # References https://github.com/satoshilabs/slips/blob/master/slip-0010.md
        master_hmac = hmac.new(StellarMnemonic.SEED_MODIFIER, digestmod=hashlib.sha512)
        master_hmac.update(seed)
        il = master_hmac.digest()[:32]
        ir = master_hmac.digest()[32:]
        path = StellarMnemonic.STELLAR_ACCOUNT_PATH_FORMAT % index
        for x in path.split("/")[1:]:
            data = (
                struct.pack("x")
                + il
                + struct.pack(">I", StellarMnemonic.FIRST_HARDENED_INDEX + int(x[:-1]))
            )
            i = hmac.new(ir, digestmod=hashlib.sha512)
            i.update(data)
            il = i.digest()[:32]
            ir = i.digest()[32:]
        return il

def get_stellar_expert_link(public_key):
    # You can create a Stellar.expert link based on the public key
    return f"https://stellar.expert/explorer/public/account/{public_key}"



@login_required
def create_account(request):
    # Check if the user has already created an account
    existing_account = StellarAccount.objects.filter(user=request.user).first()

    if existing_account:
        # If the user already has an account, redirect to the account view
        return redirect('view_account', account_pk=existing_account.pk)

    if request.method == 'POST':
        # If the form is submitted with a username, create the account
        form = UsernameForm(request.POST)
        if form.is_valid():
            # Get the authenticated user's username
            username = form.cleaned_data['username']

            # Check if the username is already in use
            if StellarAccount.objects.filter(username=username).exists():
                messages.error(request, 'Username already in use. Please choose another.')
                return render(request, 'create_account.html', {'form': form})

            # Generate a new Stellar mnemonic
            stellar_mnemonic = StellarMnemonic()
            mnemonic = stellar_mnemonic.generate()

            # Generate a new Stellar key pair
            keypair = Keypair.random()

            # Extract the public key and secret key
            public_key = keypair.public_key
            secret_key = keypair.secret

            # Generate the federation address using the provided username
            federation_address = f"{username}*zingypay.com"  # Adjust the federation address format as needed

            # Connect to the Stellar main network (replace with the main network Horizon URL)
            server = Server(horizon_url="https://horizon.stellar.org")  # Use the main network Horizon URL
            network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE  # Use the main network passphrase

            # Fetch a funded account from the Stellar main network (replace with funded account details)
            funded_account = server.load_account("GCLCIGPIF52BY3ASVR4QBLCZ7BHDYZRTAT75UYPSR4EXTI5KLUXHS2YG")

            # Create the new account transaction
            transaction = (
                TransactionBuilder(
                    source_account=funded_account,
                    network_passphrase=network_passphrase,
                    base_fee=100,
                )
                .append_create_account_op(
                    destination=public_key,
                    starting_balance="1"  # Amount of XLM to fund the new account with
                )
                .append_set_options_op(
                    home_domain="zingypay.com"  # Set the home domain
                )
                .set_timeout(30)
                .build()
            )

            # Sign the transaction with the funded account's secret key
            transaction.sign("SBCA53JJFZMMWTTF5GAS66EXYDOJTXPI5GKGVQCVE3Y66T6WSNA6S6OW")

            # Submit the transaction to create the new account
            response = server.submit_transaction(transaction)
            transaction_hash = response["hash"]

            # Fetch the balance from the Stellar network
            account = server.accounts().account_id(public_key).call()
            balance = account['balances'][0]['balance'] if 'balances' in account and account['balances'] else '0'

            # Create a new StellarAccount object and save it to the database
            stellar_account = StellarAccount(
                user=request.user,
                public_key=public_key,
                secret_key=secret_key,
                mnemonic=mnemonic,
                transaction_hash=transaction_hash,
                balance=balance,
                federation_address = f"{username}*zingypay.com",
                stellar_expert_link=get_stellar_expert_link(public_key),  # Generate Stellar.expert link
                username=username  # Save the provided username as the federation address
            )
            stellar_account.save()

            return redirect('view_account', account_pk=stellar_account.pk)
    else:
        # If the user is not logged in or the form is not submitted, display the form
        form = UsernameForm()

    return render(request, 'create_account.html', {'form': form})

# ...
def beautify_asset_code(asset_code):
    # Add logic to beautify or colorize the asset code here
    # For example, you can add styling or apply colors to the code
    return f"<span style='color: blue; font-weight: bold;'>{asset_code}</span>"



def beautify_asset_code(asset_code):
    # Add logic to beautify or colorize the asset code here
    # For example, you can add styling or apply colors to the code
    return f"<span style='color: blue; font-weight: bold;'>{asset_code}</span>"


def get_beautified_image_url(asset_code):
    # You can return a URL to a beautified or colored image here
    # For example, you can generate an image URL with a colored background and the asset code as text
    # Replace 'COLOR_CODE' with your desired color code (e.g., 'ff0000' for red)
    return f"https://dummyimage.com/100x100/ff0000/ffffff.png&text={asset_code}"



def get_asset_info(asset_code, issuer):
    try:
        # Use the issuer's public key to fetch the issuer's account details from the Stellar network
        server = Server(horizon_url="https://horizon.stellar.org")
        issuer_account = server.accounts().account_id(issuer).call()

        # Get the issuer's home domain from the account data
        issuer_domain = issuer_account.get("home_domain")

        # Check if issuer_domain is a valid domain using regular expressions
        if issuer_domain and re.match(r'^[a-zA-Z0-9.-]+$', issuer_domain):
            # Valid domain, retrieve the image URL from the asset_info
            toml_url = f"https://{issuer_domain}/.well-known/stellar.toml"
            response = requests.get(toml_url)

            if response.status_code == 200:
                toml_data = toml.loads(response.text)
                assets = toml_data.get("CURRENCIES", [])

                for asset_info in assets:
                    if asset_info.get("code") == asset_code:
                        image_url = asset_info.get("image", None)
                        if image_url:
                            return {
                                "name": asset_info.get("name", "Unknown Currency"),
                                "ticker": asset_code,
                                "image_url": image_url,
                                "issuer": issuer,
                                "home_domain": issuer_domain,
                            }

        # If issuer_domain is not valid, or fetching toml fails, use a beautified image
        return {
            "name": "Unknown Currency",
            "ticker": asset_code,
            "image_url": get_beautified_image_url(asset_code),
            "issuer": issuer,
            "home_domain": "Unknown",
        }

    except Exception as e:
        # Handle any exceptions that may occur during the request or account retrieval
        print(f"Error retrieving asset information: {str(e)}")

    # Return default information if asset info is not found
    return {
        "name": "Unknown Currency",
        "ticker": asset_code,
        "image_url": "https://example.com/unknown.png",
        "issuer": issuer,
        "home_domain": "Unknown",
    }



def fetch_asset_info_from_toml_urls(asset_code, issuer, toml_urls):
    for toml_url in toml_urls:
        try:
            # Send an HTTP GET request to the TOML URL
            response = requests.get(toml_url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the TOML data from the response
                toml_data = toml.loads(response.text)

                # Extract asset information from the TOML data
                assets = toml_data.get("CURRENCIES", [])

                for asset_info in assets:
                    if asset_info.get("code") == asset_code and asset_info.get("issuer") == issuer:
                        return asset_info

        except requests.exceptions.RequestException as e:
            # Handle any exceptions that may occur during the request
            print(f"Error retrieving asset information from TOML URL {toml_url}: {e}")

    return None

def fetch_asset_info_from_home_domain(asset_code, issuer):
    try:
        # Construct the home domain URL
        home_domain_url = f"https://{issuer}"

        # Send an HTTP GET request to the home domain URL
        response = requests.get(home_domain_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data from the response (if applicable)
            asset_info = response.json()

            if asset_info:
                return asset_info

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Error retrieving asset information from home domain {home_domain_url}: {e}")

    return None

# Function to fetch currency details from StellarTerm API
def get_currency_details(asset_code, asset_issuer):
    try:
        # Build the URL to fetch currency details based on asset code and issuer
        url = f"https://api.stellarterm.com/v1/ticker.json?asset_code={asset_code}&issuer={asset_issuer}"

        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            if 'name' in data and 'ticker' in data and 'image' in data:
                # Extract currency details from the API response
                return {
                    "name": data['name'],
                    "ticker": data['ticker'],
                    "image_url": data['image'],
                }
    except Exception as e:
        print(f"Error fetching currency details: {str(e)}")

    # If fetching currency details fails, return default values
    return {"name": "Unknown Currency", "ticker": asset_code, "image_url": image_url}


@login_required
def view_account(request, account_pk):
    try:
        stellar_account = StellarAccount.objects.get(pk=account_pk)

        # Get the username from the stellar_account object
        username = stellar_account.username  # Assuming the username is already set correctly

        # Connect to the Stellar main network (replace with the main network Horizon URL)
        server = Server(horizon_url="https://horizon.stellar.org")

        # Fetch account details from the Stellar network
        account = server.accounts().account_id(stellar_account.public_key).call()

        # Initialize lists to store balances and assets
        balances = []

        for balance in account['balances']:
            balance_amount = balance['balance']
            asset_code = balance.get('asset_code', 'XLM')
            asset_issuer = balance.get('asset_issuer')

            # Fetch asset information from Stellar.toml or StellarTerm API
            asset_info = get_asset_info(asset_code, asset_issuer)

            balances.append({
                'amount': balance_amount,
                'currency': {
                    'name': asset_info['name'],
                    'ticker': asset_code,
                    'image_url': asset_info['image_url'],
                }
            })

        context = {
            'stellar_account': stellar_account,
            'balances': balances,
            'federation_address': f"{username}*zingypay.com"
        }

    except StellarAccount.DoesNotExist:
        # Handle the case where the account is not found
        context = {'stellar_account': None}

    return render(request, 'account_details.html', context)




# Define a function to submit a transaction with retries
def submit_transaction_with_retry(transaction, max_retries=3, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            response = server.submit_transaction(transaction)
            return response
        except BadRequestError as e:
            if "transaction" in e.result_codes and e.result_codes["transaction"] == "tx_too_late":
                # Transaction was submitted too late, retry after a delay
                retries += 1
                time.sleep(retry_delay)
            else:
                # Handle other BadRequestError cases
                raise
    raise Exception("Transaction submission failed after retries")

# Usage
try:
    response = submit_transaction_with_retry(transaction)
    transaction_hash = response["hash"]
    # Handle successful transaction submission
except Exception as e:
    # Handle transaction submission failure
    pass  # You can add your error handling code here if needed




# AFRO ICO/SALE LOGIC

# Initialize Stellar SDK and Paystack API (replace with your credentials)
STELLAR_SERVER = Server("https://horizon.stellar.org")
SECRET_KEY = "SBCA53JJFZMMWTTF5GAS66EXYDOJTXPI5GKGVQCVE3Y66T6WSNA6S6OW"  # Replace with your issuer's secret key
PAYSTACK_SECRET_KEY = "sk_live_3af6fcdcd5a0c34064d4dbce95f29313bc705261"  # Replace with your Paystack secret key

# Define the fixed exchange rate (1 OSO = $0.50 USD)
FIXED_OSO_TO_USD_RATE = 0.5

# Define the exchange rate for USD to NGN
USD_TO_NGN_RATE = 820

# Define the asset you want to send
asset = Asset("OSO", "GAEESZVR52HUAHPOJZYWMWS7TYLSPS46IAK3ZDT7HTFBULDVOYUNEWCC")  # Replace with your actual asset details


@login_required
def initialize_payment(request):
    if request.method == "POST":
        # Get data from the submitted form
        email = request.POST.get("email")
        amount_in_usd = float(request.POST.get("amount"))  # Amount in USD

        # Convert the amount from USD to NGN
        amount_in_naira = amount_in_usd * USD_TO_NGN_RATE

        # Generate a unique reference for the payment
        reference = 'OSOICO_' + str(int(time.time()))

        # Create the payment request using Paystack API
        paystackapi.secret = PAYSTACK_SECRET_KEY

        payment_response = paystackapi.Transaction.initialize(
            email=email,
            amount=amount_in_naira * 100,  # Convert to kobo (Paystack's currency unit)
            reference=reference,
            currency="NGN"  # Payment currency is NGN
        )

        if payment_response.status:
            # Payment request successful, store payment details and redirect to Paystack payment page
            # You can store payment details in your database if needed
            # For example:
            payment = Payment(user=request.user, amount_ngn=amount_in_naira, payment_reference=reference)
            payment.save()

            # Redirect the user to the Paystack payment page
            return redirect(payment_response.data['authorization_url'])
        else:
            # Payment request failed, return an error response
            return HttpResponse("Payment request failed.")

    # Handle other HTTP methods or provide a fallback response
    return HttpResponse("Invalid HTTP method or action.")


# Paystack callback endpoint
def paystack_callback(request):
    if request.method == "POST":
        # Parse the Paystack callback data (you may need to adapt this based on Paystack's callback format)
        data = request.POST.get("data")
        data = json.loads(data)
        
        # Extract the paid amount from the Paystack callback data in NGN
        user_paid_amount_in_naira = data["amount"]  # Amount paid in NGN

        # Determine the destination (Stellar public key or federation address) provided by the user
        destination = request.POST.get("destination")

        # Check if the provided destination is a federation address
        if re.match(r'^[\w\.\*\-]+\*[\w\.\*\-]+$', destination):
            # Destination is a federation address, resolve it to get the associated Stellar public key
            try:
                response = FederationServer().resolve(destination)
                user_stellar_public_key = response["account_id"]
            except Exception as e:
                # Handle federation resolution error
                return HttpResponse(f"Federation resolution error: {str(e)}")
        else:
            # Destination is a direct Stellar public key
            user_stellar_public_key = destination

        # Convert the paid amount from NGN to USD
        user_paid_amount_in_usd = user_paid_amount_in_naira / USD_TO_NGN_RATE

        # Calculate the token amount based on the user's paid amount in USD
        token_amount_in_oso = user_paid_amount_in_usd / FIXED_OSO_TO_USD_RATE

        # Create and submit the Stellar transaction with the calculated token amount in OSO
        source_keypair = Keypair.from_secret(SECRET_KEY)
        transaction = (
            TransactionBuilder(source_account=STELLAR_SERVER.load_account(source_keypair.public_key))
            .append_payment_op(destination=user_stellar_public_key, amount=str(token_amount_in_oso), asset=OSO_ASSET)
            .build()
        )
        transaction.sign(source_keypair)
        response = STELLAR_SERVER.submit_transaction(transaction)

        if response["successful"]:
            # Transaction successful, save the transaction details to the database
            user = User.objects.get(stellar_public_key=user_stellar_public_key)
            currency = Currency.objects.get(code="OSO")  # Replace with the appropriate currency code
            transaction = Payment(
                user=user,
                amount_ngn=user_paid_amount_in_naira,
                amount_oso=token_amount_in_oso,
                payment_reference=reference,
            )
            transaction.save()

            # Convert OSO to AFRO
            amount_afro = convert_oso_to_afro(token_amount_in_oso)

            # Save the conversion details in the database
            conversion = TokenConversion(
                user=user,
                amount_oso=token_amount_in_oso,
                amount_afro=amount_afro,
            )
            conversion.save()

            # Redirect the user to a page showing their token balance or transaction history
            return redirect("transaction_history")
        else:
            # Transaction failed, handle error and display an error message
            return HttpResponse("Payment successful, but token transfer failed. Please contact support.")
    else:
        # Handle invalid HTTP methods
        return HttpResponse("Invalid HTTP method.")


# Function to convert OSO to AFRO based on your desired rate
def convert_oso_to_afro(token_amount_in_oso):
    # Define the conversion rate from OSO to AFRO
    OSO_TO_AFRO_RATE = 1.0  # Example rate: 1 OSO = 1 AFRO

    # Calculate the equivalent amount in AFRO
    equivalent_amount_in_afro = token_amount_in_oso * OSO_TO_AFRO_RATE

    return equivalent_amount_in_afro


# View to display the payment form
@login_required
def payment_form(request):
    # Render the payment form template
    return render(request, 'payment_form.html')


