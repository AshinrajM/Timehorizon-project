from django.db import models


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(upload_to="category", blank=True)
    # slug = models.SlugField(max_length=200, blank=True, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=500, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="brand", blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, unique=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    description = models.TextField(max_length=400, blank=True)
    image = models.ImageField(upload_to="product", blank=True)
    quantity = models.IntegerField()
    available = models.BooleanField(default=True)
    created_date = models.DateField(auto_now=True)
    updated_date = models.DateField(auto_now=True)
    image1 = models.ImageField(upload_to="product1", blank=True)
    image2 = models.ImageField(upload_to="product2", blank=True)
    image3 = models.ImageField(upload_to="product3", blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )
    sub = models.ForeignKey(
        SubCategory, on_delete=models.SET_NULL, blank=True, null=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=True)
    # slug = models.SlugField(max_length=200, blank=True, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name


class Banner(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="bannerImage", blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
