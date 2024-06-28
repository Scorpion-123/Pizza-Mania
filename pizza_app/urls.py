from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', home_page, name="home_page"),
    path('about/', about, name='about_page'),
    path('contact/', contact, name='contact_page'),

    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name="logout_user"),

    path('add_to_cart/<int:pk>/<str:retrace_location>/', add_to_cart, name="add_to_cart"),
    path('cart/', user_cart, name="user_cart"),
    path('delete_from_cart/<int:pk>/', delete_from_cart, name="delete_from_cart"),

    path('make_payment/', make_payment, name='make_payment'),
    path('confirm_payment/', confirm_payment, name='confirm_payment'),
    path('payment_successful/<int:order_id>/', payment_successful, name='payment_successful'),
]