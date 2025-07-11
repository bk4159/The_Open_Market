from django.shortcuts import render
from .models import *

def store(request):
    """
    Render the store page.
    """
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)

def cart(request):
    """
    Render the cart page.
    """
    if request.user.is_authenticated:
        customer = request.user.customer
        # either create new order or get existing order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'getCartTotal': 0, 'getCartItems': 0}

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)

def checkout(request):
    """
    Render the checkout page.
    """
    if request.user.is_authenticated:
        customer = request.user.customer
        # either create new order or get existing order
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'getCartTotal': 0, 'getCartItems': 0}
    
    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)
