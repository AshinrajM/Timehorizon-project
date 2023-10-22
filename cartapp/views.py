from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from .models import *
from orderapp.models import *
from userapp.models import Address, CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone


# Create your views here.
@login_required(login_url="signin")
def cart(
    request, total=0, quantity=0, cart_items=None, delivery_charge=0, grand_total=0
):
    context = {}
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                "product__selling_price"
            )
        else:
            return redirect("signin")
        for cart_item in cart_items:
            total += cart_item.product.selling_price * cart_item.quantity
            quantity += cart_item.quantity
        if total < 1000 and total > 1:
            delivery_charge = 99
        grand_total = total + delivery_charge
    except ObjectDoesNotExist:
        pass

    try:
        coupon = Coupon.objects.filter(active=True)
        if "coupon" in request.session:
            used_coupon_id = request.session["coupon"]
            used_coupon = Coupon.objects.get(id=used_coupon_id)
            grand_total -= used_coupon.discount
            context = {
                "used_coupon": used_coupon,
                "coupon": coupon,
                "total": total,
                "quantity": quantity,
                "cart_items": cart_items,
                "delivery_charge": delivery_charge,
                "grand_total": grand_total,
            }
        else:
            # used_coupon = None
            context = {
                "coupon": coupon,
                "total": total,
                "quantity": quantity,
                "cart_items": cart_items,
                "delivery_charge": delivery_charge,
                "grand_total": grand_total,
            }
        return render(request, "product/cart.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/cart.html", context)


@login_required(login_url="signin")
def coupon_validate(request):
    coupon = 0
    if "coupon" in request.session:
        messages.error(request, "one coupon already applied")
        return redirect("cart")

    my_user = request.user
    cart = Cart.objects.get(user=my_user)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.selling_price * cart_item.quantity

    current_time = timezone.now()  # to get current time and date

    try:
        if request.POST["coupon"]:
            coupon_rec = request.POST["coupon"]
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_rec)
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid search attempt")
                return redirect("cart")

            if current_time > coupon.valid_at:
                coupon.active = False
                coupon.save()
            elif current_time < coupon.valid_from:
                messages.error(request, "coupon not active")
                return redirect("cart")
            try:
                Order.objects.get(used_coupon=coupon)
                messages.error(request, "coupon already used")
                return redirect("cart")
            except ObjectDoesNotExist:
                pass

            if coupon:
                if coupon.min_amount > total:
                    messages.error(request, "can't apply coupon")
                    return redirect("cart")

                if not coupon.active:
                    messages.error(request, "coupon is expired")
                    return redirect("cart")

                request.session["coupon"] = coupon.id
                request.session.save()
                messages.success(request, "coupon applied")
                return redirect("cart")
    except Exception as e:
        print(e)
        return redirect("cart")


@login_required(login_url="signin")
def coupon_clear(request):
    if "coupon" in request.session:
        del request.session["coupon"]
        return redirect("cart")


@login_required(login_url="signin")
def add_cart(request, product_id):
    my_user = request.user

    user = CustomUser.objects.get(id=my_user.id)
    product = Product.objects.get(id=product_id)

    if product.quantity < 1:
        messages.error(request, "no more items available")
        return redirect("shop")
    if "user" in request.session:
        try:
            cart = Cart.objects.get(user=user)

        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            if product.quantity - cart_item.quantity > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "no more items to add")
                return redirect("cart")
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()
        return redirect("cart")
    else:
        return redirect("signin")


@login_required(login_url="signin")
def remove_cart(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_items = CartItem.objects.filter(cart=cart)
        total = 0
        for cart_i in cart_items:
            total += cart_i.product.selling_price * cart_i.quantity
        if cart_item.quantity > 1:
            total -= cart_item.product.selling_price
            if "coupon" in request.session:
                used_coupon_id = request.session["coupon"]
                used_coupon = Coupon.objects.get(id=used_coupon_id)
                if total < used_coupon.min_amount:
                    del request.session["coupon"]
            cart_item.quantity -= 1
            cart_item.save()

        else:
            return redirect("cart")
    except Exception as e:
        print(e)
        return redirect("cart")


@login_required(login_url="signin")
def full_remove(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        item_total = cart_item.product.selling_price * cart_item.quantity
        cart_items = CartItem.objects.filter(cart=cart)
        total = 0
        for cart_i in cart_items:  # using few codes for managing coupons
            total += cart_i.product.selling_price * cart_i.quantity

        if "coupon" in request.session:
            used_coupon_id = request.session["coupon"]
            used_coupon = Coupon.objects.get(id=used_coupon_id)
            total -= item_total
            if total < used_coupon.min_amount:
                del request.session["coupon"]
        cart_item.delete()
        return redirect("cart")

    except Exception as e:
        print(e)
        return redirect("cart")


@login_required(login_url="signin")
def check_out(
    request, total=0, quantity=0, cart_items=None, delivery_charge=0, grand_total=0
):
    my_user = request.user
    try:
        user = CustomUser.objects.get(id=my_user.id)
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        if not cart_items:
            return HttpResponse(False)
        addresses = Address.objects.filter(user=user.id)
        for cart_item in cart_items:
            total += cart_item.product.selling_price * cart_item.quantity
            quantity += cart_item.quantity
        if total < 1000 and total > 1:
            delivery_charge = 99
        grand_total = total + delivery_charge

        # used_coupon = None
        if "coupon" in request.session:
            id = request.session["coupon"]
            used_coupon = Coupon.objects.get(id=id)
            grand_total -= used_coupon.discount

            context = {
                "used_coupon": used_coupon,
                "user": user,
                "total": total,
                "quantity": quantity,
                "cart_items": cart_items,
                "delivery_charge": delivery_charge,
                "grand_total": grand_total,
                "addresses": addresses,
            }
        else:
            context = {
                "user": user,
                "total": total,
                "quantity": quantity,
                "cart_items": cart_items,
                "delivery_charge": delivery_charge,
                "grand_total": grand_total,
                "addresses": addresses,
            }
        return render(request, "product/checkout.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/checkout.html", context)


@login_required(login_url="signin")
def wishlist(request):
    context = {}
    if request.user.is_authenticated:
        try:
            my_user = request.user
            user = CustomUser.objects.get(id=my_user.id)
            wishlist = Wishlist.objects.filter(user=user)
            context = {"wishlist": wishlist}
            return render(request, "product/wishlist.html", context)
        except Exception as e:
            print(e)
            return render(request, "product/wishlist.html", context)
    else:
        return redirect("signin")


@login_required(login_url="signin")
def add_wishlist(request, product_id):
    my_user = request.user
    try:
        user = CustomUser.objects.get(id=my_user.id)
        product = Product.objects.get(id=product_id)
        if Wishlist.objects.filter(user=user, product=product).exists():
            return redirect("wishlist")
        wishlist = Wishlist.objects.create(user=user, product=product)
        wishlist.save()
        messages.success(request, "product added to wishlist")
        return redirect("wishlist")
    except Exception as e:
        print(e)
        return redirect("home")


@login_required(login_url="signin")
def delete_wishlist(request, wishlist_id):
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
        wishlist.delete()
        return redirect("wishlist")
    except Exception as e:
        print(e)
        return redirect("wishlist")
