
from django.urls import path
from . import views

urlpatterns = [

    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart,  name='add_to_cart'),
    path('subtract_quantity/<int:product_id>/', views.subtract_quantity, name='subtract_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart')

]