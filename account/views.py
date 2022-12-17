from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
import time
from django.contrib.auth.decorators import login_required

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
        messages.success(request, 'Registration Successfull!')
        return redirect('register')

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
            return redirect('home')
        else:
            messages.error(request, 'Invalid Login Credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):

    auth.logout(request)
    messages.success(request, 'You are now logged out.')
    return redirect('login')
