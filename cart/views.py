from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
tax_percentage = 18

def getVariations(data, product):
    
    product_variations = []
    for key, val in data.items():

        try:
            variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=val)
            product_variations.append(variation)
        except:
            pass
    return product_variations

def cart(request):
    
    total, tax, grand_total = 0, 0, 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=get_current_cart(request))
            cart_items = CartItem.objects.filter(cart=cart)
        total = 0
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
        tax = tax_percentage * total / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = []
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context=context)

@login_required(login_url='login')
def checkout(request):
    
    total, tax, grand_total = 0, 0, 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=get_current_cart(request))
            cart_items = CartItem.objects.filter(cart=cart)
        total = 0
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
        tax = tax_percentage * total / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = []
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context)

def get_current_cart(request):

    if not request.session.session_key:
        request.session.create()
    
    return request.session.session_key


def add_to_cart(request, product_id):

    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == 'POST':
        product_variations = getVariations(request.POST, product)

    if request.user.is_authenticated:
        item_in_cart = CartItem.objects.filter(product=product, user=request.user)
        if item_in_cart:

            items = CartItem.objects.filter(product=product, user=request.user)

            for item in items:

                variation = item.variation.all()
                if list(variation) == product_variations:
                    item.quantity += 1
                    item.save()
                    return redirect('cart')
        
        item = CartItem.objects.create(
            product=product,
            user=request.user,
            quantity=1,
        )
        for variation in product_variations:
            item.variation.add(variation)
        item.save()
    else:

        try:
            cart = Cart.objects.get(cart_id=get_current_cart(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=get_current_cart(request),
            )
            cart.save()
            
        item_in_cart = CartItem.objects.filter(product=product, cart=cart)
        if item_in_cart:

            items = CartItem.objects.filter(product=product, cart=cart)

            for item in items:

                variation = item.variation.all()
                if list(variation) == product_variations:
                    item.quantity += 1
                    item.save()
                    return redirect('cart')
        
        item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1,
        )
        for variation in product_variations:
            item.variation.add(variation)
        item.save()

    return redirect('cart')

def subtract_quantity(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product_variations = []
    if request.method == 'POST':
        product_variations = getVariations(request.POST, product)
    
    if request.user.is_authenticated:
        items = CartItem.objects.filter(product=product, user=request.user)
    else:    
        cart = Cart.objects.get(cart_id=get_current_cart(request))
        items = CartItem.objects.filter(product=product, cart=cart)

    for item in items:

        variation = item.variation.all()
        if list(variation) == product_variations:
            item.quantity -= 1
            if item.quantity == 0:
                item.delete()
            else:
                item.save()
            break
    return redirect('cart')

def remove_from_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product_variations = []
    if request.method == 'POST':
        product_variations = getVariations(request.POST, product)
    
    if request.user.is_authenticated:
        items = CartItem.objects.filter(product=product, user=request.user)
    else:    
        cart = Cart.objects.get(cart_id=get_current_cart(request))    
        items = CartItem.objects.filter(product=product, cart=cart)

    for item in items:

        variation = item.variation.all()
        if list(variation) == product_variations:
            item.delete()
            break
    return redirect('cart')

