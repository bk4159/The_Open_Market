from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from requests.auth import HTTPBasicAuth
import json
import datetime
import requests

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

#API endpoint to update item in cart
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

#API endpoint to process order
def processOrder(request):
    # unique transaction id based on timestamp
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

# TODO: refactor repeated code for obtaining access token
#API endpoint to create PayPal order
def processPaypalOrder(request):
    data = json.loads(request.body)
    total = f"{float(data.get('total')):.2f}"  # Ensure total is formatted as a string with 2 decimal places

    #choose base URL by environment
    base = "https://api-m.sandbox.paypal.com"

    #obtain access token
    token_url = f"{base}/v1/oauth2/token"
    try:
        token_resp = requests.post(
            token_url,
            auth=HTTPBasicAuth(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            data={'grant_type': 'client_credentials'},
            headers={'Accept': 'application/json'}
        )
        token_resp.raise_for_status()
    except requests.RequestException as exc:
        print("PayPal token request failed:", exc)
        return JsonResponse({"error": "failed to obtain paypal token"}, status=502)

    token_data = token_resp.json()
    access_token = token_data.get('access_token')
    if not access_token:
        print("No access_token in PayPal response:", token_data)
        return JsonResponse({"error": "no paypal access token"}, status=502)

    #create order with Authorization header
    create_order_url = f"{base}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{ "amount": { "currency_code": "CAD", "value": total } }]
    }

    try:
        resp = requests.post(create_order_url, headers=headers, json=payload)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print("PayPal create order failed:", exc)
        return JsonResponse({"error": "failed to create paypal order"}, status=502)

    order_data = resp.json()
    print("PayPal create order response:", order_data)

    #TODO: store order_data['id'] etc. in  Order model (add this to database)

    return JsonResponse(order_data)

# API endpoint to capture PayPal order
def capturePaypalOrder(request, orderId):
    #choose base URL by environment
    base = "https://api-m.sandbox.paypal.com"

    #obtain access token (client_credentials)
    token_url = f"{base}/v1/oauth2/token"
    try:
        token_resp = requests.post(
            token_url,
            auth=HTTPBasicAuth(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            data={'grant_type': 'client_credentials'},
            headers={'Accept': 'application/json'}
        )
        token_resp.raise_for_status()
    except requests.RequestException as exc:
        print("PayPal token request failed:", exc)
        return JsonResponse({"error": "failed to obtain paypal token"}, status=502)

    token_data = token_resp.json()
    access_token = token_data.get('access_token')
    if not access_token:
        print("No access_token in PayPal response:", token_data)
        return JsonResponse({"error": "no paypal access token"}, status=502)

    #capture order with Authorization header
    capture_order_url = f"{base}/v2/checkout/orders/{orderId}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        resp = requests.post(capture_order_url, headers=headers)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print("PayPal capture order failed:", exc)
        return JsonResponse({"error": "failed to capture paypal order"}, status=502)

    capture_data = resp.json()
    print("PayPal capture order response:", capture_data)

    return JsonResponse(capture_data)
