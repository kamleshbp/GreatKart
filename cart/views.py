from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.http import HttpResponse
# Create your views here.
tax_percentage = 18

def cart(request):
    
    total, tax, grand_total = 0, 0, 0
    try:
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

def get_current_cart(request):

    if not request.session.session_key:
        request.session.create()
    
    return request.session.session_key


def add_to_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    try:
        cart = Cart.objects.get(cart_id=get_current_cart(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=get_current_cart(request),
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=0
        )

    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

def subtract_quantity(request, product_id):

    cart = Cart.objects.get(cart_id=get_current_cart(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_from_cart(request, product_id):

    cart = Cart.objects.get(cart_id=get_current_cart(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')
