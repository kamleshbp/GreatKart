from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
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
# Create your views here.

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

        # Send confirmation email

        current_site = get_current_site(request)
        mail_subject = 'Please activate your account'
        body = render_to_string('accounts/account_activation_email.html', {
            'user': user,
            'domain': current_site,
            'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        to_email = email
        send_email = EmailMessage(subject=mail_subject, body=body, to=[to_email])
        send_email.send(fail_silently=True)
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
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')   
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
    

@login_required(login_url='login')
def dashboard(request):

    return render(request, 'accounts/dashboard.html')