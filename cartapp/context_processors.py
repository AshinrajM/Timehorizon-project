from .models import Cart, CartItem, Wishlist
from django.contrib.auth.models import AnonymousUser


def counter(request):
    item_count = 0
    if "admin" in request.path:
        return {}
    else:
        try:
            # cart = Cart.objects.filter(user=request.user)
            # cart_items = CartItem.objects.all().filter(cart=cart[:1])
            # for cart_item in cart_items:
            #     item_count += cart_item.quantity
            if not isinstance(request.user, AnonymousUser):
                cart = Cart.objects.filter(user=request.user)
                if cart.exists():
                    cart_items = CartItem.objects.filter(cart=cart.first())
                    for cart_item in cart_items:
                        item_count += cart_item.quantity
        except Cart.DoesNotExist:
            item_count = 0
    return dict(item_count=item_count)


def wishlist_counter(request):
    wishlist_item_count = 0
    if "admin" in request.path:
        return {}
    else:
        try:
            if not isinstance(request.user, AnonymousUser):
                wishlist = Wishlist.objects.filter(user=request.user)
                if wishlist:
                    wishlist_item_count = wishlist.count()
        except Wishlist.DoesNotExist:
            wishlist_item_count = 0
    return dict(wishlist_item_count=wishlist_item_count)
