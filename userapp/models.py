from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class CustomUser(User):
    mobile = models.BigIntegerField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    wallet = models.DecimalField(default=0, decimal_places=2, max_digits=8)
    referral = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.first_name


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.BigIntegerField(blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    street = models.CharField(max_length=200, blank=True, null=True)
    near_by_location = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class UserWallet(models.Model):
    TRANSACTION_TYPES = (
        ("credited", "Credited"),
        ("deduction", "Deduction"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.first_name
