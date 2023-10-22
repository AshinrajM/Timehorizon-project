from django.db import models
from userapp.models import CustomUser, Address
from cartapp.models import *
from productapp.models import *
from .models import *


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.payment_id)


class Order(models.Model):
    STATUS = (
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Ready to Deliver", "Ready to Deliver"),
        ("Cancelled", "Cancelled"),
        ("Return Requested", "Return Requested"),
        ("Return Request Rejected", "Return Request Rejected"),
        ("Returned", "Returned"),
    )
    REASON = (
        ("Accidently ordered", "Accidently ordered"),
        ("No longer needed", "No longer needed"),
        ("Delivery address changed", "Delivery address changed"),
    )
    RETURN = (
        ("Damaged product", "Damaged product"),
        ("Accidently ordered", "Accidently ordered"),
        ("No longer needed", "No longer needed"),
        ("Delivery address changed", "Delivery address changed"),
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_total = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    payable_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    wallet_amount_used = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True, default=0
    )
    status = models.CharField(max_length=30, choices=STATUS, default="Confirmed")
    cancel_reason = models.CharField(
        max_length=100, choices=REASON, null=True, blank=True
    )
    return_reason = models.CharField(
        max_length=100, choices=RETURN, null=True, blank=True
    )
    is_returned = models.BooleanField(default=False)
    refund_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True, default=0
    )
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    used_coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return str(self.order_number)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True)
    product_price = models.FloatField(blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
