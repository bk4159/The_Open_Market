from django.shortcuts import render

def store(request):
    """
    Render the store page.
    """
    context = {}
    return render(request, 'store/store.html', context)

def cart(request):
    """
    Render the cart page.
    """
    context = {}
    return render(request, 'store/cart.html', context)

def checkout(request):
    """
    Render the checkout page.
    """
    context = {}
    return render(request, 'store/checkout.html', context)
