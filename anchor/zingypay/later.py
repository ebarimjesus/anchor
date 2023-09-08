# Function to fetch live market rates
def get_live_market_rates(base_asset_code, quote_asset_code):
    order_book = STELLAR_SERVER.orderbook(base_asset_code, quote_asset_code).call()
    top_bid = order_book["bids"][0]["price"]
    top_ask = order_book["asks"][0]["price"]
    market_rate = (float(top_bid) + float(top_ask)) / 2
    return market_rate



# Initialize the Stellar server
def calculate_exchange_rate(request):
    if request.method == "POST":
        source_asset_code = request.POST.get("source_asset")
        destination_asset_code = request.POST.get("destination_asset")

        try:
            # Fetch the order book for the source and destination assets
            order_book = STELLAR_SERVER.orderbook(
                Asset.native() if source_asset_code == "XLM" else Asset(source_asset_code, "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"),
                Asset.native() if destination_asset_code == "XLM" else Asset(destination_asset_code, "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
            ).call()
            top_bid = order_book["bids"][0]["price"]

            # Calculate the exchange rate
            if source_asset_code == "XLM":
                exchange_rate = float(top_bid)
            else:
                # Create a path payment to calculate the rate
                path_payment = STELLAR_SERVER.strict_send_paths(
                    Asset(source_asset_code, "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"),
                    "1",  # Amount of source asset to send
                    Keypair.from_secret("SBCA53JJFZMMWTTF5GAS66EXYDOJTXPI5GKGVQCVE3Y66T6WSNA6S6OW"),  # Replace with your sender's secret key
                    Asset(destination_asset_code, "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV"),
                    destination_amount=amount,  # Amount of destination asset to receive
                    path=[Asset.native()] if source_asset_code == "XLM" else [Asset(source_asset_code, "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")]
                )
                path_payment_response = path_payment.fetch()
                exchange_rate = float(path_payment_response["destination_amount"])

            # Return the exchange rate as JSON
            return JsonResponse({"success": True, "exchange_rate": exchange_rate})
        except Exception as e:
            # Handle any errors that may occur while calculating the exchange rate
            return JsonResponse({"success": False, "error_message": str(e)})
    else:
        # Render the form template for GET requests
        return render(request, 'exchange_rate_form.html')



def fetch_data_with_retry(url, params=None, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            
            # Check if the response status code indicates success (e.g., 200 OK)
            if response.status_code == 200:
                return response.json()  # Parse and return the JSON data
                
            # If the response status code is not 200, raise an exception
            response.raise_for_status()
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
        
        # Wait for a moment before the next retry
        time.sleep(retry_delay)
    
    # If all retries fail, return an error response (you can customize this error response)
    return {"error": "Failed to fetch data after multiple retries"}

# Example usage:
try:
    # Define the query parameters for the order book
    order_book_params = {
        "selling_asset_type": "native",
        "buying_asset_type": "credit_alphanum4",
        "buying_asset_code": "AFRO",
        "buying_asset_issuer": "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV",
        "limit": 4
    }

    # Construct the order book URL
    order_book_url = "https://horizon.stellar.org/order_book"

    # Fetch the order book data with retry mechanism
    order_book_data = fetch_data_with_retry(order_book_url, params=order_book_params)

    print("Order Book Data:")
    print(order_book_data)
except Exception as e:
    print("Error:", e)



# Define the asset you want to send (AFRO tokens)
asset = Asset("AFRO", "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV")

# Function to retrieve the user's AFRO token balance from your database
def get_user_afro_balance(user_stellar_public_key):
    # Replace this with your database query logic to retrieve the user's AFRO token balance
    # For example, if you have a User model with a token_balance field:
    user = User.objects.get(stellar_public_key=user_stellar_public_key)
    user_afro_balance = user.token_balance
    return user_afro_balance

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
        # Replace 'XLM' and 'AFRO' with the desired trading pair (e.g., 'XLM' for Lumens and 'AFRO' for AFRO tokens)
        response = requests.get("https://horizon.stellar.org/order_book", params={"selling_asset_type": "native", "buying_asset_type": "credit_alphanum4", "buying_asset_code": "AFRO", "buying_asset_issuer": "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV"})
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
                user = User.objects.get(stellar_public_key=user_stellar_public_key)
                currency = Currency.objects.get(code="AFRO")  # Replace with the appropriate currency code
                transaction = Transaction(
                    user=user,
                    currency=currency,
                    amount=token_amount
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



# View to initiate a payment
def initialize_payment(request):
    if request.method == "POST":
        # Get data from the submitted form
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        # Generate a unique reference for the payment
        reference = 'AFROICO_' + str(int(time.time()))

        # Create the payment request using Paystack API
        paystackapi.secret = PAYSTACK_SECRET_KEY

        payment_response = paystackapi.Transaction.initialize(
            email=email,
            amount=amount * 100,  # Convert to kobo (Paystack's currency unit)
            reference=reference,
            currency="NGN"  # Adjust the currency as needed
        )

        if payment_response.status:
            # Payment request successful, store payment details and redirect to Paystack payment page
            # You can store payment details in your database if needed
            # For example:
            payment = Payment(user=request.user, amount=amount, reference=reference)
            payment.save()

            # Redirect the user to the Paystack payment page
            return redirect(payment_response.data['authorization_url'])
        else:
            # Payment request failed, return an error response
            return JsonResponse({"success": False, "error_message": "Payment request failed."})

    # Handle other HTTP methods or provide a fallback response
    return JsonResponse({"success": False, "error_message": "Invalid HTTP method or action."})

# Define a view to display the form for initiating payment
def payment_form(request):
    # Render the payment form template
    return render(request, 'payment_form.html')

