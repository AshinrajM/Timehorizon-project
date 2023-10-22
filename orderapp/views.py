from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from decimal import Decimal
from cartapp.models import *
from userapp.models import *
from orderapp.models import *
from .models import *
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
import datetime
import random
import razorpay
import uuid


# Create your views here.


@login_required(login_url="signin")
def place_order(request, quantity=0):
    if "user" in request.session:
        user_id = request.user
        user = CustomUser.objects.get(id=user_id.id)
    context = {}
    try:
        if request.method == "POST":
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items:
                return HttpResponse(True)
            for cart_item in cart_items:
                quantity += cart_item.quantity
            amount = request.POST.get("total")
            del_chg = request.POST.get("delivery_charge")
            delivery_charge = Decimal(del_chg)
            total = Decimal(amount)
            grand_total = request.POST.get("grand_total")
            grand_amount = 0
            amount_to_be_paid = 0
            wallet = 0
            used_wallet_amount = 0

            new_address = request.POST.get("selected_address")

            if request.POST.get("walletcheck"):
                wallet = Decimal(user.wallet)
                grand_total = Decimal(grand_total)
                # cart.wallet_added = True       field on cart for variable
                if wallet <= grand_total:
                    grand_amount = grand_total - wallet
                    amount_to_be_paid = grand_total - wallet
                    used_wallet_amount = grand_total - amount_to_be_paid
                else:
                    grand_amount = 0
                    amount_to_be_paid = 0
                    used_wallet_amount = grand_total

            else:
                grand_amount = grand_total
                amount_to_be_paid = grand_total
                # cart.wallet_added = False     field on cart for variable
            # cart.save()                       field on cart for variable
            address = Address.objects.get(id=new_address)

            payment_method = request.POST["paymentMethod"]
        context = {
            "grand_amount": grand_amount,
            "amount_to_be_paid": amount_to_be_paid,
            "used_wallet_amount": used_wallet_amount,
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "delivery_charge": delivery_charge,
            "grand_total": grand_total,
            "address": address,
            "payment_method": payment_method,
        }
        return render(request, "product/confirm_order.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/confirm_order.html", context)


@cache_control(no_cache=True, no_store=True)
@login_required(login_url="signin")
def confirm_order(request, total=0, grand_total=0, delivery_charge=0, quantity=0):
    context = {}
    # confirm payment and order
    if "user" in request.session:
        session_user = request.user
        user = CustomUser.objects.get(id=session_user.id)
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        return HttpResponse(True)
    if not cart_items:
        return redirect("shop")
    for cart_item in cart_items:
        total += cart_item.product.selling_price * cart_item.quantity
        quantity += cart_item.quantity
    if total < 1000 and total > 1:
        delivery_charge = 99
        grand_total = total + delivery_charge
    else:
        # delivery_charge = 0
        grand_total = total

    # grand amount is the variable used to handle wallet instead of solving grand total
    grand_amount = request.POST["grand_amount"]
    wallet_amount = request.POST["used_wallet_amount"]
    used_wallet_amount = Decimal(wallet_amount)
    if request.method == "POST":
        address_id = request.POST.get("selected_address")
        address = Address.objects.get(id=address_id)
        if address:
            new_order = Order()
            new_order.user = user
            new_order.address = address

            # new_order.order_total = grand_total
            new_order.order_total = grand_total
            new_order.amount_paid_for_order = grand_amount
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            rand = str(random.randint(1111111, 9999999))
            order_number = current_date + rand
            new_order.order_number = order_number
            new_order.save()
            payment = Payment()
            payment.user = user

            wallet = user.wallet

            user.wallet = wallet - used_wallet_amount  # wallet amount handling
            user.save()
            if used_wallet_amount != 0:
                new = UserWallet.objects.create(  # wallet history
                    user=user, transaction_type="deducted", amount=used_wallet_amount
                )
                new.save()

            new_order.wallet_amount_used = used_wallet_amount
            new_order.save()
            payment_method = request.POST.get("paymentMethod")
            if payment_method == "cash_on_delivery":
                payment.payment_method = "COD"  # Cash on delivery payment method
                payment.payment_id = order_number + "COD"
                new_order.payable_amount = grand_amount
            else:
                # Handle other payment methods (replace with your logic)
                # payment.payment_method = "razorpay"
                payment_id = request.POST.get("payment_id")
                payment.payment_id = payment_id
                payment.payment_method = payment_method

                payment.amount_paid = grand_amount
                new_order.payable_amount = grand_amount

                payment.is_paid = True
                payment.save()
            new_order.save()
            payment.save()
            new_order.payment = payment
            new_order.save()
            user.save()
            # Handle order items and product quantities
            items = CartItem.objects.filter(cart=cart)
            for item in items:
                product = Product.objects.get(id=item.product.id)
                order_product = OrderProduct()
                order_product.product = item.product
                order_product.product_price = item.product.selling_price
                order_product.quantity = item.quantity
                order_product.is_ordered = True
                order_product.order = new_order
                order_product.payment = payment
                order_product.save()

                # Update product quantity
                product.quantity -= order_product.quantity
                product.save()

            if "coupon" in request.session:
                used_coupon_id = request.session["coupon"]
                used_coupon = Coupon.objects.get(id=used_coupon_id)
                new_order.used_coupon = used_coupon
                new_order.save()
                del request.session["coupon"]

            # Clear the cart and return a success message based on the payment method

            cart.delete()
            cart_items.delete()
            context = {
                "order_number": order_number,
            }
            if payment_method == "cash_on_delivery":
                return render(request, "product/ordersuccess.html", context)
            else:
                return JsonResponse(
                    {
                        "status": "Your order has been placed successfully ",
                        "order_number": order_number,
                    }
                )

    #     return render(request, "product/ordersuccess.html")

    # else:
    #     return redirect("check_out")


def proceed_to_pay(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = 0
    grand_total = 0
    delivery_charge = 0
    grand_amount = float(request.GET.get("grand_amount"))
    print(grand_amount)
    for cart_item in cart_items:
        total += cart_item.product.selling_price * cart_item.quantity
    if total < 1000 and total > 1:
        delivery_charge = 99
        grand_total = float(total + delivery_charge)
    else:
        grand_total = float(total)
    return JsonResponse(
        {
            "grand_amount": grand_total,
            "final_amount": grand_amount,
        }
    )


def order_status(request, order_id):
    try:
        if request.method == "POST":
            status = request.POST.get("order_status")
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
        return redirect("admin_order")
        
    except Exception as e:
        print(e)
        return redirect("admin_order")


def orders(request):
    context = {}
    my_user = request.user
    try:
        user = CustomUser.objects.get(id=my_user.id)
        order = Order.objects.filter(user=user).order_by("created_at")

        order_items = []
        order_details = []
        for i in order:
            order_products = OrderProduct.objects.filter(order=i)
            # Create a list of product details for this order
            order_product_info = []
            for order_product in order_products:
                product_info = {
                    "product_image": order_product.product.image,
                    "product_name": order_product.product.name,
                    "quantity": order_product.quantity,
                    "product_price": order_product.product.selling_price,
                }
                order_product_info.append(product_info)

            # Append the order details and associated product details to the list

            order_details.append(
                {
                    "order_number": i.order_number,
                    "order_total": i.order_total,
                    "status": i.status,
                    "order_products": order_product_info,
                }
            )

        context = {
            "order": order,
            "order_details": order_details,
            "order_items": order_items,
        }
        return render(request, "user/orders.html", context)
    except Exception as e:
        print(e)
        return render(request, "user/orders.html", context)
        


def order_details(request, order_id):
    context = {}
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderProduct.objects.filter(order=order)
        order_total = Decimal(order.order_total)
        shipping_charge = 0
        if order_total < 1000 and order_total < 902:
            shipping_charge = 99
        else:
            shipping_charge = "Free"
        context = {
            "shipping_charge": shipping_charge,
            "orders": order,
            "order_items": order_items,
        }
        return render(request, "product/order_details.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/order_details.html", context)


def cancel_order(request, cancel_order_id):
    user_session = request.user
    user = CustomUser.objects.get(id=user_session.id)

    order = Order.objects.get(id=cancel_order_id)
    cancel_reason = request.POST.get("cancel_reason")

    order.status = "Cancelled"
    order.cancel_reason = cancel_reason
    order.save()
    total = order.payable_amount
    wallet_amount_used = order.wallet_amount_used

    total_decimal = Decimal(total)  # decimal field is used for wallet
    payment_method = order.payment.payment_method
    if payment_method == "Paid by razorpay":
        user.wallet += total_decimal + wallet_amount_used
        user.save()
        order.refund_amount += total_decimal + wallet_amount_used
        order.save()
        new = UserWallet.objects.create(
            user=user, transaction_type="credited", amount=total_decimal
        )
        new.save()
    else:
        user.wallet += wallet_amount_used
        user.save()
        new = UserWallet.objects.create(
            user=user, transaction_type="credited", amount=wallet_amount_used
        )
        new.save()
        order.refund_amount += wallet_amount_used
        order.save()
    order_products = OrderProduct.objects.filter(order=order.id)
    if order.status == "Cancelled":
        for order_product in order_products:
            product = Product.objects.get(id=order_product.product.id)
            product.quantity += order_product.quantity
            product.save()
    order.save()
    return redirect("orders")


def return_order(request, order_id):
    user_session = request.user
    user = CustomUser.objects.get(id=user_session.id)
    return_reason = request.POST.get("return_reason")
    order = Order.objects.get(id=order_id)
    order.status = "Return Requested"
    order.return_reason = return_reason
    order.save()

    # --------------handle return request start
    # wallet_amount_used = order.wallet_amount_used

    # total = order.order_total
    # total_decimal = Decimal(total)
    # user.wallet += total_decimal
    # user.save()

    # new = UserWallet.objects.create(
    #     user=user, transaction_type="credited", amount=total_decimal
    # )
    # new.save()

    # order.refund_amount = total_decimal
    # order.save()

    # --------------handle return request end

    order_products = OrderProduct.objects.filter(order=order.id)
    if order.status == "Cancelled":
        for order_product in order_products:
            product = Product.objects.get(id=order_product.product.id)
            product.quantity += order_product.quantity
            product.save()
    order.save()
    return redirect("orders")


def success(request, order_number):
    context = {
        "order_number": order_number,
    }
    return render(request, "product/ordersuccess.html", context)


def generate_invoice(request, order_id):
    context = {}
    order = Order.objects.get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    invoice_number = f"INV-{order.order_number}"
    template = get_template("user/invoice.html")
    each_product = []
    for item in order_products:
        each_product.append(item.quantity * item.product.selling_price)
    context = {
        "order": order,
        "order_products": order_products,
        "invoice_number": invoice_number,
        "each_product": each_product,
    }
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{invoice_number}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response
