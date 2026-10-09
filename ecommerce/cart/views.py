from django.shortcuts import render , redirect , get_object_or_404
from store.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def add_to_cart(request , product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart' , {})
    key = str(product.id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    messages.success(request , 'Add to Cart Successfully')
    return redirect('home')

@login_required
def remove_from_cart(request , product_id):
    cart = request.session.get('cart' , {})
    key = str(product_id)
    
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        messages.success(request , 'Product remove form cart')
        
    return redirect('cart_detail')

@login_required
def increase_quantity(request , product_id):
    cart = request.session.get('cart' , {})
    key = str(product_id)
    
    if key in cart:
        cart[key] += 1
        request.session['cart'] = cart
    return redirect('cart_detail')  

@login_required
def decrease_quantity(request , product_id):
    cart = request.session.get('cart' , {})
    key = str(product_id)
    
    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]
        request.session['cart'] = cart
    
    return redirect('cart_detail')
            



@login_required  
def cart_detail(request):
    cart = request.session.get('cart' , {})
    items = []
    total = 0
    
    for product_id , quantity in cart.items():
        product = get_object_or_404(Product , id=product_id )
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product':product,
            'quantity':quantity,
            'subtotal':subtotal,
        })
        
    return render(request , 'cart/cart_detail.html' , { 'items': items , 'total':total})




