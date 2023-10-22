from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages


# Create your views here.


def home(request):
    if "admin" in request.session:
        return redirect("dashboard")
    context = {}
    try:
        product = (
            Product.objects.all().filter(active=True).order_by("-created_date")[:4]
        )
        category = Category.objects.all().filter(active=True)[:4]
        brand = Brand.objects.all()[:3]
        banner = Banner.objects.all()
        banner1 = Banner.objects.get(name="Cover image top")
        banner2 = Banner.objects.get(name="Middle banner image")
        banner3 = Banner.objects.get(name="End banner image")
        context = {
            "category": category,
            "product": product,
            "brand": brand,
            "banner1": banner1,
            "banner2": banner2,
            "banner3": banner3,
        }
        return render(request, "product/home.html", context)
    except Exception as e:
        print(e)
        return render(request, "product/home.html", context)


def shop(request):
    if "admin" in request.session:
        return redirect("dashboard")
    
    context = {}

    try:
        sub_categories = SubCategory.objects.all().filter(active=True)
        categories = Category.objects.all().filter(active=True)
        product_list = Product.objects.all().filter(active=True)

        paginator = Paginator(product_list, 3)
        try:
            page = int(request.GET.get("page", "1"))
        except:
            page = 1
        try:
            product = paginator.page(page)
        except (EmptyPage, InvalidPage):
            product = paginator.page(paginator.num_pages)

        context = {
            "product": product,
            "categories": categories,
            "sub_categories": sub_categories,
        }
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def product_search(request):
    context = {}

    product = Product.objects.filter(active=True)
    categories = Category.objects.all().filter(active=True)
    product_list = product
    try:
        if "search" in request.GET:
            search = request.GET["search"]
            if search:
                product = Product.objects.filter(
                    Q(name__icontains=search, active=True)
                    | Q(brand__name__icontains=search)
                    | Q(category__name__icontains=search)
                )
                product_count = product.count()
                product_list = product
                context = {
                    "search": search,
                    "product": product,
                    "product_count": product_count,
                    "categories": categories,
                }
            else:
                context = {
                    "product": product,
                    "categories": categories,
                }
        return render(request, "product/shop.html", context)
    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def shop_by_category(request, category_id):
    context = {}

    categories = Category.objects.all().filter(active=True)
    category = Category.objects.get(id=category_id)
    try:
        if request.method == "POST":
            product = Product.objects.filter(category=category_id, active=True)
        else:
            product = Product.objects.all().filter(active=True)

        context = {
            "product": product,
            "categories": categories,
            "category": category,
        }
        messages.success(request, "showing - ")
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def shop_by_brand(request, brand_id):
    context = {}

    try:
        brnad = Brand.objects.get(id=brand_id)
        product = Product.objects.filter(brand=brnad)

        context = {
            "product": product,
        }
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def category_filter(request, id):
    context = {}
    try:
        category = Category.objects.get(id=id)
        product = Product.objects.filter(category=category.id)
        context = {"product": product}
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def product_detail(request, product_id):
    if "admin" in request.session:
        return redirect("dashboard")
    context = {}
    try:
        products = Product.objects.get(id=product_id, active=True)
        related = Product.objects.exclude(id=product_id, active=True)[:4]
        context = {"products": products, "related": related}
        return render(request, "product/product-details.html", context)
    except Exception as e:
        print(e)
        return render(request, "product/product-details.html", context)


def filter_by_price(request):
    context = {}
    
    try:
        product = Product.objects.filter(active=True)
        categories = Category.objects.all().filter(active=True)
        minimum = request.GET["min"]
        maximum = request.GET["max"]
        if minimum > maximum:
            messages.error(request, "choose range properly")
            return redirect("shop")
        if minimum and maximum:
            product = Product.objects.filter(
                selling_price__lt=maximum, selling_price__gt=minimum, active=True
            ).order_by("selling_price")

        context = {
            "product": product,
            "categories": categories,
            "minimum": minimum,
            "maximum": maximum,
        }
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def ascending_sort(request):
    context = {}

    try:
        product = Product.objects.filter(active=True).order_by("selling_price")
        categories = Category.objects.all().filter(active=True)
        ascending = True
        context = {
            "product": product,
            "categories": categories,
            "ascending": ascending,
        }
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)


def descending_sort(request):
    context = {}

    try:
        product = Product.objects.filter(active=True).order_by("-selling_price")
        categories = Category.objects.all().filter(active=True)
        context = {
            "product": product,
            "categories": categories,
        }
        return render(request, "product/shop.html", context)

    except Exception as e:
        print(e)
        return render(request, "product/shop.html", context)
