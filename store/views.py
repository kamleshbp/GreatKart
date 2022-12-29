from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import get_current_cart
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ReviewRating
from django.contrib import messages
from .forms import ReviewForm
from orders.models import OrderProduct
# Create your views here.

def store(request, category_slug=None):

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(is_available=True, category=category).order_by('id')
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
    
    # product_counts = len(products)
    paginator = Paginator(products, 1 if category_slug else 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_counts = products.count()
    return render(request, 'store/store.html', context={
        'products': paged_products,
        'product_counts': product_counts
    })


def product_detail(request, category_slug, product_slug):

    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    return render(request, 'store/product_detail.html', context={
        'product': product,
        'orderproduct': orderproduct,
        'reviews': reviews,
    })

def search(request):

    products, product_counts = [], 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) or Q(product_name__icontains=keyword))
            product_counts = products.count()
    context = {
        'products': products,
        'product_counts': product_counts
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
    return redirect(url)

