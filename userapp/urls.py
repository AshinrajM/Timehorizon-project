from django.urls import path
from . import views

urlpatterns = [
    path("", views.signin, name="signin"),
    path("register/", views.register, name="register"),
    path("signout/", views.signout, name="signout"),
    path(
        "otp-verification/<int:user_id>/<str:referral>/",
        views.otp_verification,
        name="otp",
    ),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path(
        "forgot-password-otp/<int:user_id>",
        views.forgot_password_otp,
        name="forgot_password_otp",
    ),
    path(
        "change_password/<int:user_id>", views.change_password, name="change_password"
    ),
    path("add-address/", views.add_address, name="add_address"),
    path(
        "delete-address/<int:address_id>", views.delete_address, name="delete_address"
    ),
    path("address-book/", views.address_book, name="address_book"),
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("reset-password<int:user_id>/", views.reset_password, name="reset_password"),
    path("wallet-history/", views.wallet_history, name="wallet_history"),
    path("about/", views.about, name="about"),
]
