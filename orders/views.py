from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import OrderForm

from cart.models import CartItem
from cart.views import tax_percentage


from datetime import date
from .models import Order, Payment, OrderProduct

from store.models import Product
# Create your views here.

import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def payments(request):

    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

    return render(request, 'orders/payments.html')


def place_order(request):

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():

            order = form.save()

            order.user = request.user

            cart_items = CartItem.objects.filter(user=request.user)
            total = 0
            for cart_item in cart_items:
                total += cart_item.product.price * cart_item.quantity
            tax = total * tax_percentage / 100

            order.order_total = total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.order_number = date.today().strftime('%Y%m%d') + str(order.id)

            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': total + tax,
            }
            return render(request, 'orders/payments.html', context)

    return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        
        return redirect('home')







