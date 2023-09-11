
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

