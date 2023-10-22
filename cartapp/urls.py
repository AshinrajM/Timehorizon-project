from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add-cart/<int:product_id>/", views.add_cart, name="add_cart"),
    path("remove-cart/<int:product_id>/", views.remove_cart, name="remove_cart"),
    path("full_remove/<int:product_id>/", views.full_remove, name="full_remove"),
    path("checkout/", views.check_out, name="check_out"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add-wishlist/<int:product_id>/", views.add_wishlist, name="add_wishlist"),
    path(
        "delete-wishlist/<int:wishlist_id>/",
        views.delete_wishlist,
        name="delete_wishlist",
    ),
    path("coupon-validate/", views.coupon_validate, name="coupon_validate"),
    path("coupon-clear/", views.coupon_clear, name="coupon_clear"),
]
