from django.urls import path
from zingypay import views

urlpatterns = [
    # Other URL patterns
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
]

