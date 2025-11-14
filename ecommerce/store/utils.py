import json
from .models import *

def get_cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except KeyError:
        cart = {}
    items = []
    order = {'getCartTotal': 0, 'getCartItems': 0, 'requiresShipping': False}
    cartItems = order['getCartItems']

    for i in cart:
        try:
            #parse through cart cookie to create required objects
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            productTotal = product.price * cart[i]['quantity']
            order['getCartTotal'] += productTotal
            order['getCartItems'] += cart[i]['quantity']

            # TODO: refactor to use a class instead of dictionary
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'getTotal': productTotal
            }
            items.append(item)

            if not product.digital:
                order['requiresShipping'] = True
        except Product.DoesNotExist:
            print(f"Product with id {i} does not exist.")
            continue
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

def get_cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        # either create new order or get existing order for the specified customer, and that isn't completed
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.getCartItems
    else:
        cookie_data = get_cookie_cart(request)
        cartItems = cookie_data['cartItems']
        order = cookie_data['order']
        items = cookie_data['items']
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

def process_guest_order(request, data):
    user_form_data = data['userFormData']
    
    #get data from cookie for guest user
    name = user_form_data['name']
    email = user_form_data['email']
    cookie_data = get_cookie_cart(request)
    items = cookie_data['items']

    #create customer object
    #if guest customer with this email already exists, get that customer instead of creating new one
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    #create order object
    order = Order.objects.create(customer=customer, complete=False)

    #create order items
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    
    return customer, order
