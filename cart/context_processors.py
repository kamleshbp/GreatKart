from .models import Cart, CartItem
from .views import get_current_cart
def counter(request):

    items_in_cart = 0
    try:
        cart = Cart.objects.get(cart_id=get_current_cart(request))
        cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            items_in_cart += cart_item.quantity
            
    except Cart.DoesNotExist:
        pass
    return dict(items_in_cart=items_in_cart)