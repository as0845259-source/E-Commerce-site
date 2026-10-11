from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from .models import Product , Category
from django.contrib.auth.decorators import login_required


@login_required
def home(request, category_slug=None):
    products = Product.objects.all()
    categories = Category.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    query = request.GET.get('q' , '').strip()
    if query:
        products = products.filter(name__icontains=query)
            

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'active_category': category_slug,
    })

@login_required
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_details.html', {'product': product})
