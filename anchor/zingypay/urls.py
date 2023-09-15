from django.urls import path
from zingypay import views

urlpatterns = [
    # Other URL patterns
    path('initialize_payment/', views.initialize_payment, name='initialize_payment'),
    # path('paystack_callback/', views.paystack_callback, name='paystack_callback'),
    # path('calculate_exchange_rate/', views.calculate_exchange_rate, name='calculate_exchange_rate'),
    path('payment-form/', views.payment_form, name='payment_form'),
    path('create_account/', views.create_account, name='create_account'),
    # path('resolve_stellar_address/', views.resolve_stellar_address, name='resolve_stellar_address'),
    path('view_account/<int:account_pk>/', views.view_account, name='view_account'),
    path('initiate-flutterwave-payment/', views.initiate_flutterwave_payment, name='initiate-flutterwave-payment'),
    path('flutterwave-callback/', views.flutterwave_payment_callback, name='flutterwave-callback'),
    path('initiate-paystack-payment/', views.initiate_paystack_payment, name='initiate_paystack_payment'),
    path('paystack_payment_callback/', views.paystack_payment_callback, name='paystack_payment_callback'),
    path('initiate-stellar-payment/', views.initiate_stellar_payment, name='initiate_stellar_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),

    
    # path('import-stellar-account/', views.import_stellar_account, name='import_stellar_account'),
]


