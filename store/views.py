from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
# Create your views here.

def store(request, category_slug=None):

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(is_available=True, category=category)
    else:
        products = Product.objects.filter(is_available=True)
    
    # product_counts = len(products)
    product_counts = products.count()
    return render(request, 'store/store.html', context={
        'products': products,
        'product_counts': product_counts
    })


def product_detail(request, category_slug, product_slug):

    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e        
    return render(request, 'store/product_detail.html', context={
        'product': product
    })
