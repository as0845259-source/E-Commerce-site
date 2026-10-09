from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .forms import OrderForm
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required



@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_detail')

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = total
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity'],
                )

            request.session['cart'] = {}
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': items,
        'total': total,
    })

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request , 'orders/my_orders.html' , {'orders':orders})