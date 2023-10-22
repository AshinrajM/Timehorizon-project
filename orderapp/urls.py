from django.urls import path
from . import views

urlpatterns = [
    path("", views.place_order, name="place_order"),
    path("order-status/<int:order_id>/", views.order_status, name="order_status"),
    path("orders/", views.orders, name="orders"),
    path(
        "cancel-order/<int:cancel_order_id>/", views.cancel_order, name="cancel_order"
    ),
    path("return-order/<int:order_id>", views.return_order, name="return_order"),
    path("confirm-order/", views.confirm_order, name="confirm_order"),
    path("proceed-to-pay/", views.proceed_to_pay, name="proceed_to_pay"),
    path("order-details/<int:order_id>", views.order_details, name="order_details"),
    path('success/<str:order_number>/',views.success,name="success"),
    path('generate-invoice/<int:order_id>/',views.generate_invoice, name='generate_invoice'),
]
