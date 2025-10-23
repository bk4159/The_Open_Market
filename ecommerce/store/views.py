from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *
from .utils import get_cart_data, process_guest_order

def store(request):
    """
    Render the store page.
    """
    data = get_cart_data(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    """
    Render the cart page.
    """
    data = get_cart_data(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    """
    Render the checkout page.
    """
    data = get_cart_data(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

# API endpoint to update item in cart
def updateItem(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    #request.user is the User model instance
    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    # either create new order or get existing order for the specified customer, and that isn't completed
    order, order_created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, order_item_created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    
    # persist changes to database
    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()
    return JsonResponse("Item was added", safe=False)

# API endpoint to process order
def processOrder(request):
    # Unique transaction id based on timestamp
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    user_form_data = data['userFormData']
    shipping_form_data = data['shippingFormData']


    if request.user.is_authenticated:
        customer = request.user.customer
        # either create new order or get existing order for the specified customer, and that isn't completed
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = process_guest_order(request, data)
    
    total = float(user_form_data['total'])
    order.transaction_id = transaction_id

    #make sure the total passed from the form matches the total in the order (no manipulation)
    if total == float(order.getCartTotal):
        order.complete = True
    order.save()

    if order.requiresShipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=shipping_form_data['address'],
            city=shipping_form_data['city'],
            state=shipping_form_data['state'],
            zipcode=shipping_form_data['zipcode'],
            country=shipping_form_data['country']
        )

    return JsonResponse("Payment complete!", safe=False)
