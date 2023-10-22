from django.db import models
from productapp.models import Product
from userapp.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    date_added = models.DateField(auto_now_add=True)
    wallet_added = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.selling_price * self.quantity

    def __str__(self):
        return self.product.name


class Wishlist(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.product.name


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=25, blank=True, null=True)
    discount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    min_amount = models.IntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    valid_from = models.DateTimeField()
    valid_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    description = models.TextField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.coupon_code
