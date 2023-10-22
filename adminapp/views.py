from django.shortcuts import render, redirect
from django.http import HttpResponse
from productapp.models import *
from userapp.models import CustomUser
from orderapp.models import *
from userapp.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from django.core.exceptions import ObjectDoesNotExist

from xhtml2pdf import pisa
from django.template.loader import render_to_string

# from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum, F, Case, When, IntegerField, Q
from datetime import date, datetime, timedelta
from django.db.models import Count
from django.db.models.functions import ExtractMonth


# from user.models import Custom_user


# Create your views here.


@cache_control(no_cache=True, no_store=True)
def admin_login(request):
    if "admin" in request.session:
        return redirect("dashboard")
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, username=email, password=password)
            if user:
                if user.is_staff or user.is_superuser:
                    request.session["admin"] = email
                    login(request, user)
                    return redirect("dashboard")
                else:
                    messages.error(request, "add proper credentials")
                    return redirect("admin_login")
            else:
                messages.error(request, "add proper credentials")
                return redirect("admin_login")
        return render(request, "admin/admin_login.html")
    except Exception as e:
        print(e)
        return render(request, "admin/admin_login.html")


@staff_member_required(login_url="admin_login")
@cache_control(no_cache=True, no_store=True)
def admin_logout(request):
    logout(request)
    request.session.flush()
    return redirect("admin_login")


@staff_member_required(login_url="admin_login")
@cache_control(no_cache=True, no_store=True)
def admin_dashboard(request):
    context = {}
    try:
        income = Order.objects.filter(
            Q(status="Delivered") | Q(status="Return Request Rejected")
        ).aggregate(Sum("order_total"))["order_total__sum"]

        total_income = float(income)

        total_successfull_orders = Order.objects.filter(
            Q(status="Delivered") | Q(status="Return Request Rejected")
        ).count()
        # total_cancelled_orders = Order.objects.filter(
        #     Q(status="Cancelled") | Q(status="Returned")
        # ).count()
        refund_amount = Order.objects.filter(is_returned=True).aggregate(
            Sum("refund_amount")
        )["refund_amount__sum"]

        total_refund_amount = float(refund_amount)

        # total_profit = round(total_income * Decimal(0.20), 2)

        profit = total_income * 0.20

        total_profit = float(profit)

        user_count = CustomUser.objects.all().count()
        product_count = Product.objects.all().count()
        order_count = Order.objects.count()
        categories = Category.objects.count()
        cash_on_delivery = Order.objects.filter(payment__payment_method="COD").count()
        razor_pay = Order.objects.filter(
            payment__payment_method="Paid by razorpay"
        ).count()

        refund_amount = Order.objects.aggregate(total=Sum("refund_amount"))["total"]

        # monthly sales

        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        monthly_sales_data = (
            Order.objects.annotate(month=ExtractMonth("created_at"))
            .values("month")
            .annotate(total_sales=Count("id"))
            .order_by("month")
        )

        data = [["Month", "Sales"]]
        for sales in monthly_sales_data:
            month = sales["month"]
            total_sales = sales["total_sales"]
            month_name = month_names[month]  # Get the month name from the dictionary
            data.append([month_name, total_sales])

        # monthly sales calculation end

        cod = round((cash_on_delivery / order_count) * 100)
        razor_pay = round((razor_pay / order_count) * 100)

        requests = Order.objects.filter(status="Return Requested")

        if request.method == "POST":
            fromDate = request.POST.get("fromDate")
            toDate = request.POST.get("toDate")
            try:
                if fromDate < toDate:
                    orders_in_range = Order.objects.filter(
                        created_at__range=(fromDate, toDate)
                    )
                    context = {
                        "fromDate": fromDate,
                        "toDate": toDate,
                        "orders_in_orange": orders_in_range,
                        "income": total_income,
                        "refund_amount": refund_amount,
                        "profit": total_profit,
                        "successfull": total_successfull_orders,
                        "refund": total_refund_amount,
                        "requests": requests,
                        "monthly_sales_data": data,
                        "cod": cod,
                        "razor_pay": razor_pay,
                        "order_count": order_count,
                        "user_count": user_count,
                        "product_count": product_count,
                        "categories": categories,
                    }
                else:
                    messages.error(request, "select dates properly")
                    return redirect("dashboard")
            except Exception as e:
                print(e)
                return redirect("dashboard")
        else:
            context = {
                "income": total_income,
                "refund_amount": refund_amount,
                "profit": total_profit,
                "successfull": total_successfull_orders,
                "refund": total_refund_amount,
                "requests": requests,
                "monthly_sales_data": data,
                "cod": cod,
                "razor_pay": razor_pay,
                "order_count": order_count,
                "user_count": user_count,
                "product_count": product_count,
                "categories": categories,
            }

        return render(request, "admin/admin_dashboard.html", context)
    except Exception as e:
        print(e)
        return render(request, "admin/admin_dashboard.html", context)


def pdf_report(request):
    fromDate = request.POST["fromDate"]
    toDate = request.POST["toDate"]
    orders_in_range = Order.objects.filter(created_at__range=(fromDate, toDate))
    context = {
        "orders_in_range": orders_in_range,
        "fromDate": fromDate,
        "toDate": toDate,
    }
    html = render_to_string("admin/table_template.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="report.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        # link_callback=fetch_resources
    )

    if pisa_status.err:
        return HttpResponse("PDF generation error")

    return response


@staff_member_required(login_url="admin_login")
def admin_product(request):
    context = {}
    try:
        products = Product.objects.all()
        categories = Category.objects.all()
        sub_categories = SubCategory.objects.all()
        brands = Brand.objects.all()
        if request.method == "POST":
            search = request.POST.get("name")
            products = Product.objects.filter(name__icontains=search)
        context = {
            "products": products,
            "categories": categories,
            "sub_categories": sub_categories,
            "brands": brands,
        }
        return render(request, "admin/admin_product.html", context)
    except Exception as e:
        print(e)
        return render(request, "admin/admin_product.html", context)


@staff_member_required(login_url="admin_login")
def product_active(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if product.active == True:
            product.active = False
        else:
            product.active = True
        product.save()
        return redirect("admin_product")
    except Exception as e:
        print(e)
        return redirect("admin_product")


@staff_member_required(login_url="admin_login")
def category_active(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        if category.active == True:
            category.active = False
        else:
            category.active = True
        category.save()
        return redirect("admin_category")
    except Exception as e:
        print(e)
        return redirect("admin_category")


@staff_member_required(login_url="admin_login")
def sub_category_active(request, sub_id):
    try:
        sub_category = SubCategory.objects.get(id=sub_id)
        if sub_category.active == True:
            sub_category.active = False
        else:
            sub_category.active = True
        sub_category.save()
        return redirect("admin_sub_category")
    except Exception as e:
        print(e)
        return redirect("admin_sub_category")


@staff_member_required(login_url="admin_login")
def admin_add_product(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name").strip()
            original_price = request.POST.get("original_price")
            selling_price = request.POST.get("selling_price")

            if original_price < selling_price:
                messages.error(
                    request, "selling price has to be less than original price"
                )
                return redirect("admin_product")

            description = request.POST.get("description")
            quantity = request.POST.get("quantity")
            category = request.POST.get("category")
            category_id = Category.objects.get(name=category)
            brand = request.POST.get("brand")
            brand_id = Brand.objects.get(name=brand)
            sub_category = request.POST.get("subcategory")
            sub_category_id = SubCategory.objects.get(name=sub_category)
            image = request.FILES.get("image")
            image1 = request.FILES.get("image1")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")
            if image:
                product = Product.objects.create(
                    name=name,
                    original_price=original_price,
                    selling_price=selling_price,
                    description=description,
                    quantity=quantity,
                    category=category_id,
                    sub=sub_category_id,
                    brand=brand_id,
                    image=image,
                    image1=image1,
                    image2=image2,
                    image3=image3,
                )
                product.save()
                messages.success(request, "New product added successfully")
                return redirect("admin_product")

    except Exception as e:
        print(e)
        return redirect("admin_product")


@staff_member_required(login_url="admin_login")
def admin_edit_product(request, product_id):
    context = {}
    try:
        products = Product.objects.get(id=product_id)
        categories = Category.objects.exclude(id=products.category.id)
        sub_categories = SubCategory.objects.exclude(id=products.sub.id)

        brands = Brand.objects.exclude(id=products.brand.id)
        context = {
            "categories": categories,
            "sub_categories": sub_categories,
            "brands": brands,
            "products": products,
        }
        return render(request, "admin/admin_edit_product.html", context)
    except Exception as e:
        print(e)
        return render(request, "admin/admin_edit_product.html", context)


@staff_member_required(login_url="admin_login")
def admin_update_product(request, product_id):
    try:
        if request.method == "POST":
            new_name = request.POST.get("name")
            original_price = request.POST.get("original_price")
            selling_price = request.POST.get("selling_price")
            if original_price < selling_price:
                messages.error(
                    request, "selling price has to be less than original price"
                )
                return redirect("admin_product")

            description = request.POST.get("description")
            quantity = request.POST.get("quantity")
            category = request.POST.get("category")
            category_id = Category.objects.get(name=category)
            brand = request.POST.get("brand")
            brand_id = Brand.objects.get(name=brand)
            sub_category = request.POST.get("subcategory")
            sub_category_id = SubCategory.objects.get(name=sub_category)
            image = request.FILES.get("image")
            image1 = request.FILES.get("image1")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")

            product = Product.objects.get(id=product_id)
            product.name = new_name
            product.original_price = original_price
            product.selling_price = selling_price
            product.description = description
            product.quantity = quantity
            product.category = category_id
            product.sub = sub_category_id
            product.brand = brand_id

            if image:
                product.image = image
            else:
                product.image = product.image

            if image1:
                product.image1 = image1
            else:
                product.image1 = product.image1

            if image2:
                product.image2 = image2
            else:
                product.image2 = product.image2

            if image3:
                product.image3 = image3
            else:
                product.image3 = product.image3

            product.save()
            messages.success(request, "product details updated")
            return redirect("admin_product")

    except Exception as e:
        print(e)
        return redirect("admin_product")
    # return render(request, "admin/admin_edit_product.html")


@staff_member_required(login_url="admin_login")
def admin_user(request):
    context = {}
    try:
        users = CustomUser.objects.filter(is_staff=False)
        context = {"users": users}
        return render(request, "admin/admin_users.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_users.html", context)


@staff_member_required(login_url="admin_login")
def user_active(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.is_active == True:
            user.is_active = False
            user.save()
        else:
            user.is_active = True
            user.save()
        return redirect("admin_user")
    except Exception as e:
        print(e)
        return redirect("admin_user")


@staff_member_required(login_url="admin_login")
def admin_category(request):
    context = {}
    try:
        category = Category.objects.all()
        context = {"categories": category}
        return render(request, "admin/admin_category.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_category.html", context)


@staff_member_required(login_url="admin_login")
def admin_edit_category(request, category_id):
    context = {}
    try:
        categories = Category.objects.get(id=category_id)
        context = {"categories": categories}
        return render(request, "admin/admin_edit_category.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_edit_category.html", context)


@staff_member_required(login_url="admin_login")
def admin_update_category(request, category_id):
    category = Category.objects.get(id=category_id)
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            description = request.POST.get("description")
            image = request.FILES.get("image")

            if image:
                category.image = image
            else:
                category.image = category.image
            category.name = name
            category.description = description
            category.save()
            messages.success(request, "category updated")
            return redirect("admin_category")

    except Exception as e:
        print(e)
        return redirect("admin_category")


@staff_member_required(login_url="admin_login")
def admin_sub_category(request):
    context = {}
    try:
        sub_category = SubCategory.objects.all()
        context = {"sub_category": sub_category}
        return render(request, "admin/admin_sub_category.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_sub_category.html", context)


@staff_member_required(login_url="admin_login")
def admin_edit_sub_category(request, sub_id):
    context = {}
    try:
        sub_category = SubCategory.objects.get(id=sub_id)

        context = {"sub_category": sub_category}
        return render(request, "admin/admin_edit_sub_category.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_edit_sub_category.html", context)


@staff_member_required(login_url="admin_login")
def admin_update_sub_category(request, sub_id):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            description = request.POST.get("description")
            if name or description:
                sub_category = SubCategory(
                    id=sub_id,
                    name=name,
                    description=description,
                )
                sub_category.save()
                messages.success(request, "changed successfully")
                return redirect("admin_sub_category")
            else:
                return redirect("admin_edit_sub_category")
    except Exception as e:
        print(e)
        return redirect("admin_edit_sub_category")


@staff_member_required(login_url="admin_login")
def admin_brand(request):
    context = {}
    try:
        brands = Brand.objects.all()
        context = {
            "brands": brands,
        }
        return render(request, "admin/admin_brand.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_brand.html", context)



@staff_member_required(login_url="admin_login")
def admin_add_brand(request):
    try:
        if request.method == "POST":
            name = request.POST["name"]
            image = request.FILES["image"]
            description = request.POST["description"]
            brand = Brand()
            brand.name = name
            brand.image = image
            brand.description = description
            brand.save()
            messages.success(request, "NEW BRAND ADDED")
            return redirect("admin_brand")

    except Exception as e:
        print(e)
        return redirect("admin_brand")


@staff_member_required(login_url="admin_login")
def admin_update_brand(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    try:
        if request.method == "POST":
            name = request.POST["name"]
            image = request.FILES.get("image")
            description = request.POST["description"]
            brand.name = name
            brand.description = description
            if image:
                brand.image = image
            else:
                brand.image = brand.image
            brand.save()
            messages.success(request, "Brand updated")
            return redirect("admin_brand")

    except Exception as e:
        print(e)
        return redirect("admin_brand")


@staff_member_required(login_url="admin_login")
def admin_banner(request):
    context = {}
    try:
        banners = Banner.objects.all()
        context = {
            "banners": banners,
        }
        return render(request, "admin/admin_banner.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_banner.html", context)


@staff_member_required(login_url="admin_login")
def admin_update_banner(request, banner_id):
    try:
        banner = Banner.objects.get(id=banner_id)
        if request.method == "POST":
            image = request.FILES.get("image")
            if image:
                banner.image = image
            else:
                banner.image = banner.image
            banner.save()
            messages.success(request, "Updated Successfully")
            return redirect("admin_banner")

    except Exception as e:
        print(e)
        return redirect("admin_banner")


@staff_member_required(login_url="admin_login")
def admin_order(request):
    context = {}
    try:
        order = Order.objects.exclude(status="Return Requested").order_by("created_at")
        requests = Order.objects.filter(status="Return Requested")
        context = {
            "order": order,
            "requests": requests,
        }
        return render(request, "admin/admin_order.html", context)
    except Exception as e:
        print(e)
        return render(request, "admin/admin_order.html", context)


@staff_member_required(login_url="admin_login")
def admin_order_detail(request, order_id):
    context = {}
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderProduct.objects.filter(order=order)
        delivery_charge = 0
        if float(order.order_total) < 1000:
            delivery_charge = 99

        context = {
            "delivery_charge": delivery_charge,
            "order": order,
            "order_items": order_items,
        }
        return render(request, "admin/admin_order_detail.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_order_detail.html", context)


@staff_member_required(login_url="admin_login")
def admin_request_approve(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        user = order.user

        total = order.order_total
        total_decimal = Decimal(total)

        order.is_returned = True
        order.status = "Returned"
        order.refund_amount = total_decimal
        order.save()

        user.wallet += total_decimal
        user.save()

        new = UserWallet.objects.create(
            user=user, transaction_type="credited", amount=total_decimal
        )
        new.save()
        return redirect("admin_order")

    except Exception as e:
        print(e)
        return redirect("admin_order")


@staff_member_required(login_url="admin_login")
def admin_request_rejected(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        user = order.user
        order.status = "Return Request Rejected"
        order.save()
        return redirect("admin_order")

    except Exception as e:
        print(e)
        return redirect("admin_order")


@staff_member_required(login_url="admin_login")
def admin_coupon(request):
    context = {}
    try:
        coupon = Coupon.objects.all()
        context = {
            "coupons": coupon,
        }
        return render(request, "admin/admin_coupon.html", context)

    except Exception as e:
        print(e)
        return render(request, "admin/admin_coupon.html", context)


@staff_member_required(login_url="admin_login")
def admin_add_coupon(request):
    try:
        if request.method == "POST":
            coupon_code = request.POST["code"].strip()
            discount = request.POST["discount"]
            minimum_amount = request.POST["minimum_amount"]
            valid_from = request.POST["valid_from"]
            valid_at = request.POST["valid_at"]

            if float(discount) < 1:
                messages.error(request, "minimum discount amount should be 1")
                return redirect("admin_coupon")

            if float(discount) > float(minimum_amount):
                messages.error(request, "discount has to be less than minimum amount")
                return redirect("admin_coupon")

            if valid_from > valid_at:
                messages.error(request, "add validity range properly")
                return redirect("admin_coupon")

            coupon = Coupon.objects.create(
                coupon_code=coupon_code,
                discount=discount,
                min_amount=minimum_amount,
                valid_from=valid_from,
                valid_at=valid_at,
            )
            coupon.save()
            messages.success(request, "New coupon added successfully")
            return redirect("admin_coupon")

    except Exception as e:
        print(e)
        return redirect("admin_coupon")


@staff_member_required(login_url="admin_login")
def admin_update_coupon(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        if request.method == "POST":
            coupon_code = request.POST["code"].strip()
            new_discount = request.POST["discount"]

            if float(new_discount) < 1:
                messages.error(request, "minimum discount amount should be 1")
                return redirect("admin_coupon")

            discount = Decimal(new_discount)
            minimum_amount = int(request.POST["minimum_amount"])

            if discount >= minimum_amount:
                messages.error(request, "discount has to be less than minimum amount")
                return redirect("admin_coupon")

            valid_from = request.POST["valid_from"]
            valid_at = request.POST["valid_at"]

            if valid_from > valid_at:
                messages.error(request, "add validity range properly")
                return redirect("admin_coupon")

            coupon.coupon_code = coupon_code
            coupon.discount = discount
            coupon.min_amount = minimum_amount
            coupon.valid_from = valid_from
            coupon.valid_at = valid_at
            coupon.save()
            messages.success(request, "coupon updated successfully")
            return redirect("admin_coupon")

    except Exception as e:
        print(e)
        return redirect("admin_coupon")
