from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('process_paypal_order/', views.processPaypalOrder, name='process_paypal_order'),
    path('capture_paypal_order/<str:orderId>/', views.capturePaypalOrder, name='capture_paypal_order'),
]
