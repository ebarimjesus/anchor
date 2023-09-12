from django.urls import path
from zingypay import views

urlpatterns = [
    # Other URL patterns
    path('initialize_payment/', views.initialize_payment, name='initialize_payment'),
    path('paystack_callback/', views.paystack_callback, name='paystack_callback'),
    # path('calculate_exchange_rate/', views.calculate_exchange_rate, name='calculate_exchange_rate'),
    path('payment-form/', views.payment_form, name='payment_form'),
    path('create_account/', views.create_account, name='create_account'),
    
    path('view_account/<int:account_pk>/', views.view_account, name='view_account'),
    
    # path('import-stellar-account/', views.import_stellar_account, name='import_stellar_account'),
]


