
import os
import requests
import time
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


from .models import StellarAccount  # Import your Django model

def create_account(username):
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
            base_fee=10000,
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

    return stellar_account



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




