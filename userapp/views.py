from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Address, UserWallet
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import uuid


@cache_control(no_cache=True, no_store=True)
def register(request):
    if "admin" in request.session:
        return redirect("dashboard")
    try:
        if request.method == "POST":
            email = request.POST["email"]
            firstname = request.POST["firstname"].strip()
            lastname = request.POST["lastname"].strip()
            mobile = request.POST["mobile"]
            password = request.POST["password"]
            c_password = request.POST["c_password"]
            if not request.POST["referral"]:
                referral = "abc"
            else:
                referral = request.POST["referral"]
            if CustomUser.objects.filter(username=email).exists():
                messages.error(request, "email already exists")
                return redirect("register")
            if CustomUser.objects.filter(mobile=mobile).exists():
                messages.error(request, "mobile already exists")
                return redirect("register")
            if password != c_password:
                messages.error(request, "passwords mismatch")
                return redirect("register")
            else:
                user = CustomUser.objects.create_user(
                    username=email,
                    first_name=firstname,
                    last_name=lastname,
                    mobile=mobile,
                    password=password,
                )
                otp = get_random_string(length=6, allowed_chars="1234567890")
                subject = "Verify your account "
                message = f"Your OTP for account verification in Time_Horizon is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    email,
                ]
                send_mail(subject, message, email_from, recipient_list)
                user.otp = otp
                user.save()
                return redirect("otp", user.id, referral)

        return render(request, "user/register.html")
    except Exception as e:
        print(e)
        return render(request, "user/register.html")


def generate_ref_code():
    code = str(uuid.uuid4()).replace("-", "")[:12]
    return code


@cache_control(no_store=True, no_cache=True)
def otp_verification(request, user_id, referral):
    try:
        user = CustomUser.objects.get(id=user_id)
        try:
            referred_user = CustomUser.objects.get(referral=referral)
        except CustomUser.DoesNotExist:
            referred_user = None
        if user:
            existing_otp = user.otp
        if request.method == "POST":
            otp = request.POST.get("otp")
            if otp == existing_otp:
                user.is_verified = True
                user.save()
                if referred_user:
                    referred_user.wallet += 50
                    referred_user.save()
                    new = UserWallet.objects.create(
                        user=referred_user, transaction_type="credited", amount=50.00
                    )
                    new.save()
                referral_code = generate_ref_code()
                user.referral = referral_code
                user.save()

                return redirect("signin")
            else:
                messages.error(
                    request, "otp verification failed! check the entered details"
                )
                return redirect("otp", user_id=user_id)
        return render(request, "user/otp_verify.html")

    except Exception as e:
        print(e)
        return render(request, "user/otp_verify.html")


@cache_control(no_cache=True, no_store=True)
def signin(request):
    if "admin" in request.session:
        return redirect("dashboard")

    if "user" in request.session:
        return redirect("home")

    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, username=email, password=password)
            if user:
                user_new = CustomUser.objects.get(id=user.id)
                if user_new.is_verified == True and user.is_active == True:
                    if user.is_superuser or user.is_staff:
                        return redirect("signin")
                    else:
                        request.session["user"] = email
                        login(request, user)
                        return redirect("home")
                else:
                    messages.error(request, "add the credentials properly")
                    return redirect("signin")
            else:
                messages.error(request, "add the credentials properly")
                return redirect("signin")
        return render(request, "user/login.html")
    except Exception as e:
        return render(request, "user/login.html")


@cache_control(no_cache=True, no_store=True)
def signout(request):
    logout(request)
    return redirect("signin")


@cache_control(no_cache=True, no_store=True)
def forgot_password(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            user = CustomUser.objects.filter(username=email).first()
            if user:
                otp = get_random_string(length=6, allowed_chars="1234567890")
                user.otp = otp
                user.save()
                subject = "Verify your account"
                message = f"Your OTP for account verification in Time_Horizon is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    email,
                ]
                # return HttpResponse(user.email)
                send_mail(subject, message, email_from, recipient_list)
                return redirect("forgot_password_otp", user.id)
            else:
                messages.error(request, "email id not valid")
                return redirect("forgot_password")
        return render(request, "user/forgot_password.html")
        
    except Exception as e:
        print(e)
        return render(request, "user/forgot_password.html")


@cache_control(no_cache=True, no_store=True)
def forgot_password_otp(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    otp = user.otp
    try:
        if request.method == "POST":
            user_otp = request.POST.get("user_otp")
            if user_otp == otp:
                return redirect("change_password", user.id)
            else:
                messages.error(request, "incorrect otp")
                return redirect("forgot_password_otp")
        return render(request, "user/forgot_password_otp.html")
        
    except Exception as e:
        print(e)
        return render(request, "user/forgot_password_otp.html")


@cache_control(no_cache=True, no_store=True)
def change_password(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    try:
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("c_password")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "password changed successfully")
                return redirect("signin")
            else:
                messages.error(request, "passwords doesnt match")
                return redirect("change_password")
        return render(request, "user/change_password.html")

    except Exception as e:
        print(e)
        return render(request, "user/change_password.html")


@login_required(login_url="signin")
def add_address(request):
    my_user = request.user
    user = CustomUser.objects.get(id=my_user.id)
    try:
        if request.method == "POST":
            name = request.POST.get("name").strip()
            address = request.POST.get("address")
            district = request.POST.get("district")
            state = request.POST.get("state")
            near_by_location = request.POST.get("near_by_loc")
            street = request.POST.get("street")
            postcode = request.POST.get("postcode")
            phone = request.POST.get("phone")
            address = Address.objects.create(
                name=name,
                address=address,
                district=district,
                state=state,
                near_by_location=near_by_location,
                street=street,
                postcode=postcode,
                phone=phone,
                user=user,
            )
            address.save()
            messages.success(request, "New Address added")
            return redirect("address_book")
        return render(request, "user/add_address.html")
    except Exception as e:
        print(e)
        return render(request, "user/add_address.html")



@login_required(login_url="signin")
def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
        address.delete()
        return redirect("address_book")
    except Exception as e:
        return redirect("address_book")


@login_required(login_url="signin")
def address_book(request):
    try:
        my_user = request.user
        addresses = Address.objects.filter(user=my_user.id)
        context = {
            "addresses": addresses,
        }
        return render(request, "user/address_book.html", context)

    except Exception as e:
        print(e)
        return redirect("address_book")


@login_required(login_url="signin")
def profile(request):
    context ={}
    try:
        my_user = request.user
        user = CustomUser.objects.get(id=my_user.id)

        if "history" in request.session:
            history = request.session["history"]
            wallet_history = UserWallet.objects.filter(user=user)

            context = {
                "user": user,
                "wallet_history": wallet_history,
            }
        else:
            context = {
                "user": user,
            }
        return render(request, "user/profile.html", context)
    except Exception as e:
        print(e)
        return render(request, "user/profile.html", context)



@login_required(login_url="signin")
def reset_password(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    try:
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect("profile")
            else:
                messages.error(request, "enter matching passwords")
                return redirect("reset_password")
        return render(request, "user/reset_password.html")

    except Exception as e:
        print(e)
        return render(request, "user/reset_password.html")



@login_required(login_url="signin")
def edit_profile(request):
    try:
        my_user = request.user
        user = CustomUser.objects.get(id=my_user.id)
        context = {"user": user}
        return render(request, "user/edit_profile.html", context)
    except Exception as e:
        print(e)
        return render(request, "user/edit_profile.html", context)



@login_required(login_url="signin")
def update_profile(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            mobile = request.POST.get("mobile")
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.mobile = mobile
            user.save()
            messages.success(request, "profile details updated")
            return redirect("profile")
        except Exception as e:
            print(e)
            return redirect("profile")
            
    else:
        return redirect("edit_profile")


@login_required(login_url="signin")
def wallet_history(request):
    context = {}
    try:
        my_user = request.user
        user = CustomUser.objects.get(id=my_user.id)
        history = UserWallet.objects.filter(user=user)

        context = {"history": history}
        return render(request, "user/wallet_history.html", context)
    except Exception as e:
        print(e)
        return render(request, "user/wallet_history.html", context)

def about(request):
    return render(request, "user/about.html")
