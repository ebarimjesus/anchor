
from django.shortcuts import render, redirect
from django.http import HttpResponse
from stellar_sdk import Server, Keypair, TransactionBuilder, Asset, FederationServer
import requests
import json
import re
from .models import Transaction, UserProfile, User, StellarAccount
from .forms import DepositForm
import paystackapi  # Make sure you've installed this package


import os
import requests
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone



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
from .models import StellarAccount, User, Transaction

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
server = Server(horizon_url="https://horizon.stellar.org")  # Create the server object globally




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


@login_required
def create_account(request):
    # Get the authenticated user's username
    username = request.user.username

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
            starting_balance="0"  # Amount of XLM to fund the new account with
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

    # Create a new StellarAccount object and save it to the database
    stellar_account = StellarAccount(
        public_key=public_key,
        secret_key=secret_key,
        mnemonic=mnemonic,
        transaction_hash=transaction_hash,
        balance=0,  # Initialize balance as 0
        stellar_expert_link=get_stellar_expert_link(public_key),  # Generate Stellar.expert link
        username=username  # Save the provided username as the federation address
    )
    stellar_account.save()

    return redirect('view_account', account_id=stellar_account.pk)




def view_account(request, account_id):
    try:
        stellar_account = StellarAccount.objects.get(pk=account_id)
    except StellarAccount.DoesNotExist:
        # Handle the case where the account is not found
        stellar_account = None

    return render(request, 'account_details.html', {'stellar_account': stellar_account})



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




# ...

# Paystack callback endpoint
def paystack_callback(request):
    if request.method == "POST":
        # Parse the Paystack callback data (you may need to adapt this based on Paystack's callback format)
        data = request.POST.get("data")
        data = json.loads(data)
        
        # Extract the paid amount from the Paystack callback data
        user_paid_amount_in_fiat = data["amount"]  # Amount paid in fiat currency (e.g., NGN)

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

        # Query the Stellar DEX API to get the current token price
        # Replace 'XLM' and 'TOKEN' with the desired trading pair (e.g., 'XLM' for Lumens and 'TOKEN' for your custom token)
        response = requests.get("https://horizon.stellar.org/order_book", params={"selling_asset_type": "native", "buying_asset_type": "credit_alphanum4", "buying_asset_code": "TOKEN", "buying_asset_issuer": "ISSUER_PUBLIC_KEY"})
        if response.status_code == 200:
            order_book = response.json()
            # Extract the current best price (e.g., the highest bid)
            best_price = float(order_book["bids"][0]["price"])
            
            # Calculate the token amount based on the user's paid amount in fiat currency
            token_amount = user_paid_amount_in_fiat / best_price
            
            # Create and submit the Stellar transaction with the calculated token amount
            source_keypair = Keypair.from_secret(SECRET_KEY)
            transaction = (
                TransactionBuilder(source_account=STELLAR_SERVER.load_account(source_keypair.public_key))
                .append_payment_op(destination=user_stellar_public_key, amount=str(token_amount), asset=asset)
                .build()
            )
            transaction.sign(source_keypair)
            response = STELLAR_SERVER.submit_transaction(transaction)

            if response["successful"]:
                # Transaction successful, save the transaction details to the database
                transaction = Transaction(
                    user_stellar_public_key=user_stellar_public_key,
                    fiat_amount=user_paid_amount_in_fiat,
                    token_amount=token_amount
                )
                transaction.save()

                # Redirect the user to a page showing their token balance
                return redirect("token_balance", user_stellar_public_key=user_stellar_public_key)
            else:
                # Transaction failed, handle error and display an error message
                return HttpResponse("Payment successful, but token transfer failed. Please contact support.")
        else:
            # Handle error when querying the Stellar DEX API
            return HttpResponse("Error querying Stellar DEX API.")
    else:
        # Handle invalid HTTP methods
        return HttpResponse("Invalid HTTP method.")



# Initialize Stellar SDK and Paystack API (replace with your credentials)
STELLAR_SERVER = Server("https://horizon.stellar.org")
SECRET_KEY = "YOUR_ISSUER_SECRET_KEY"  # Replace with your issuer's secret key
PAYSTACK_SECRET_KEY = "YOUR_PAYSTACK_SECRET_KEY"  # Replace with your Paystack secret key

# Define the asset you want to send
asset = Asset("AFRO", "ISSUER_PUBLIC_KEY")  # Replace with your actual asset details

# Function to retrieve the user's AFRO token balance from your database
def get_user_afro_balance(user_stellar_public_key):
    # Replace this with your database query logic to retrieve the user's AFRO token balance
    # For example, if you have a User model with a token_balance field:
    user = User.objects.get(stellar_public_key=user_stellar_public_key)
    user_afro_balance = user.token_balance
    user_afro_balance = balance  # Replace with the actual AFRO token balance from the database
    return user_afro_balance


# Function to fetch live market rates
def get_live_market_rates(base_asset_code, quote_asset_code):
    order_book = stellar_server.orderbook(base_asset_code, quote_asset_code).call()
    top_bid = order_book["bids"][0]["price"]
    top_ask = order_book["asks"][0]["price"]
    market_rate = (float(top_bid) + float(top_ask)) / 2
    return market_rate


# Paystack callback endpoint
def deposit(request):
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            # Get the user's Stellar public key from the user profile
            user_profile = UserProfile.objects.get(user=request.user)
            user_stellar_public_key = user_profile.stellar_public_key

            # Process deposit transaction
            asset_code = form.cleaned_data['asset_code']
            amount = form.cleaned_data['amount']

            # Fetch live market rates
            market_rate = get_live_market_rates(asset_code, "XLM")  # Replace "XLM" with the base asset code

            if market_rate is not None:
                # Calculate the equivalent AFRO tokens based on the user's deposit amount and market rate
                afro_tokens = amount / market_rate

                # For Paystack integration, you can initiate a deposit request
                paystackapi.secret = PAYSTACK_SECRET_KEY
                deposit_response = paystackapi.Transaction.initialize(
                    email=request.user.email,  # Use the user's email for Paystack
                    amount=amount,
                    currency="NGN"  # Adjust the currency as needed
                )

                if deposit_response.status:
                    # Save the transaction details to the database
                    transaction = Transaction(
                        user=request.user,
                        stellar_public_key=user_stellar_public_key,
                        asset_code=asset_code,
                        amount=amount,
                        afro_tokens=afro_tokens,  # Save the calculated AFRO tokens
                        transaction_hash=deposit_response.data['reference']
                    )
                    transaction.save()

                    # Redirect the user to a page showing their AFRO token balance
                    return redirect("afro_balance", user_stellar_public_key=user_stellar_public_key)
                else:
                    return render(request, "deposit.html", {"form": form, "error_message": "Deposit failed."})
            else:
                return render(request, "deposit.html", {"form": form, "error_message": "Market rate not available."})
    else:
        form = DepositForm()
    return render(request, "deposit.html", {"form": form})



# View to display the user's AFRO token balance
def afro_balance(request, user_stellar_public_key):
    # Retrieve the user's AFRO token balance from your database based on their Stellar public key
    user_afro_balance = get_user_afro_balance(user_stellar_public_key)
    
    return render(request, "afro_balance.html", {"user_afro_balance": user_afro_balance})




def initiate_payment(request):
    if request.method == "POST":
        # Get data from the frontend
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        # Initiate the payment using Paystack API
        paystackapi.secret = 'YOUR_PAYSTACK_SECRET_KEY'  # Replace with your Paystack secret key

        # Generate a unique reference (or use a specific order ID)
        reference = 'YOUR_REFERENCE_GENERATION_LOGIC'

        # Create the payment request
        payment_response = paystackapi.Transaction.initialize(
            email=email,
            amount=amount,
            reference=reference,
            currency="NGN"  # Adjust the currency as needed
        )

        if payment_response.status:
            # Payment request successful, create a transaction record
            transaction = Transaction(
                email=email,
                amount=amount,
                reference=reference
            )
            transaction.save()

            # Return a response to the frontend indicating success
            return JsonResponse({"success": True, "payment_url": payment_response.data['authorization_url']})

        else:
            # Payment request failed, return an error response to the frontend
            return JsonResponse({"success": False, "error_message": "Payment request failed."})


def paystack_webhook(request):
    if request.method == "POST":
        # Parse the incoming JSON data from Paystack
        webhook_data = request.POST.get("data")
        data = json.loads(webhook_data)

        # Extract relevant information from the webhook data
        reference = data.get("reference")
        status = data.get("status")

        try:
            # Find the corresponding transaction in your database
            transaction = Transaction.objects.get(reference=reference)

            # Update the transaction status based on Paystack's status
            if status == "success":
                transaction.status = "completed"
                # Calculate the AFRO token amount based on the payment amount
                # You may need to fetch the current market rate for the conversion
                # For simplicity, assume a fixed rate for this example
                afro_tokens = transaction.amount / FIXED_CONVERSION_RATE  # Replace with your conversion rate
                transaction.afro_tokens = afro_tokens
            else:
                transaction.status = "failed"

            transaction.save()

            # Respond to Paystack with a success message
            return JsonResponse({"status": "success"})
        except Transaction.DoesNotExist:
            # Handle the case where the transaction doesn't exist
            return JsonResponse({"status": "error", "message": "Transaction not found"})
    else:
        # Handle invalid HTTP methods
        return JsonResponse({"status": "error", "message": "Invalid HTTP method"})



