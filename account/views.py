from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
import time
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from django.http import HttpResponse, QueryDict

from cart.models import Cart, CartItem
from cart.views import get_current_cart
from orders.models import OrderProduct

from orders.models import Order
# Create your views here.

def send_email_with_token(request, subject, user, email, email_template):

    current_site = get_current_site(request)
    body = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_email = email
    send_email = EmailMessage(subject=subject, body=body, to=[to_email])
    send_email.send(fail_silently=True)

def register(request):

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password']
        username = email.split('@')[0] + str(int(time.time()))
        user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
        user.phone_number = phone_number
        user.save()
        # messages.success(request, 'Registration Successfull!')

        # Create a user profile
        profile = UserProfile()
        profile.user_id = user.id
        profile.profile_picture = 'default/default.jpg'
        profile.save()

        # Send confirmation email
        email_template = 'accounts/account_activation_email.html'
        subject = 'Please activate your account'
        send_email_with_token(request=request, subject=subject, user=user, email=email,email_template=email_template)

        # messages.success(request, 'Email is sent for your account verification.')
        return redirect(reverse('login') + f'?command=validate&email={email}')

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(request, email=email, password=password)

        if user:
            
            cart_item_exists = CartItem.objects.filter(cart__cart_id=get_current_cart(request)).exists()
            
            # Moving the current cart_items to logged in user's cart
            if cart_item_exists:
                current_cart_items = CartItem.objects.filter(cart__cart_id=get_current_cart(request))
                existing_cart_items = CartItem.objects.filter(user=user)
                for current_cart_item in current_cart_items:
                    current_product_variations = list(current_cart_item.variation.all())
                    existing_products = existing_cart_items.filter(product=current_cart_item.product)
                    existing_product_variations = []
                    for existing_product in existing_products:
                        if list(existing_product.variation.all()) == current_product_variations:
                            existing_product.quantity += current_cart_item.quantity
                            existing_product.save()
                            break
                    else:
                        current_cart_item.user = user
                        current_cart_item.save()

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            try:
                url = request.META['HTTP_REFERER']
                query =  QueryDict(url.split('?')[1])
                if 'next' in query:
                    return redirect(query['next'])
            except:
                pass
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Login Credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):

    auth.logout(request)
    messages.success(request, 'You are now logged out.')
    return redirect('login')


def activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64)
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is now activated. You can login now.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')
    


def forgot_password(request):


    if request.method == 'POST':

        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            email_template = 'accounts/reset_password_email.html'
            subject = 'Reset your password'
            send_email_with_token(request=request, subject=subject, user=user, email=email,email_template=email_template)
            messages.success(request, 'Reset password link has been shared on your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid email address.')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def validate_reset_password(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'The reset password link has been expired!')
        return redirect('login')


def reset_password(request):

    if request.method == 'POST':
        
        if 'uid' not in request.session:
            messages.error(request, "Please enter your email to reset your password.")
            return redirect('forgot_password')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:

            uid = request.session.get('uid')
            request.session.pop('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been updated')
            return redirect('login')
        else:
            messages.error(request, 'Your password does not match')
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')


@login_required(login_url='login')
def dashboard(request):
    
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)
    

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
