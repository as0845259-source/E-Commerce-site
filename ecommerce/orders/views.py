
import stripe

from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages

from store.models import Product
from .forms import OrderForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_detail')

    items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        quantity = int(quantity)
        if quantity < 1:
            continue

        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if not items:
        return redirect('cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = total
            order.payment_status = 'pending'
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity'],
                )

            stripe.api_key = settings.STRIPE_SECRET_KEY

            try:
                session = stripe.checkout.Session.create(
                    mode='payment',

                    line_items=[
                        {
                            'price_data': {
                                'currency': 'pkr',
                                'product_data': {
                                    'name': item['product'].name,
                                },
                                'unit_amount': int(
                                    item['product'].price * 100
                                ),
                            },
                            'quantity': item['quantity'],
                        }
                        for item in items
                    ],
                    success_url=request.build_absolute_uri(
                        reverse('order_success', args=[order.id])
                    ) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(
                        reverse('checkout')
                    ),
                    client_reference_id=str(order.id),
                    metadata={'order_id': str(order.id)},
                )

                order.stripe_session_id = session.id
                order.save(update_fields=['stripe_session_id'])

                return redirect(session.url)

            except Exception as e:
                print("STRIPE ERROR:", repr(e))
                messages.error(
                    request,
                    'Payment could not be started. Please check the terminal.'
                )

    else:
        form = OrderForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    session_id = request.GET.get('session_id')

    if order.payment_status != 'paid':
        if not session_id or session_id != order.stripe_session_id:
            messages.info(request, 'Your payment has not been verified yet.')
            return redirect('my_orders')

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if (
                session.payment_status == 'paid'
                and session.metadata.order_id == str(order.id)
            ):
                order.payment_status = 'paid'
                order.save(update_fields=['payment_status'])
                request.session['cart'] = {}
            else:
                messages.info(request, 'Payment is not complete yet.')
                return redirect('my_orders')

        except stripe.error.StripeError:
            messages.error(request, 'Unable to verify payment right now.')
            return redirect('my_orders')

    return render(
        request,
        'orders/order_success.html',
        {'order': order},
    )


@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'orders/my_orders.html',
        {'orders': orders},
    )
