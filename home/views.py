from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError

from web50.settings import MY_APPS
from commerce.models import Merchant

def home(request):
    projects = [{"name": name, "url": f'{name}:index'} for name in MY_APPS]
    return render(request, "home/home.html", {'projects': projects})

def login_view(request, login_temp, login_redirect):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        print(user)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(login_redirect)
        else:
            return render(request, login_temp, {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, login_temp)

def logout_view(request, logout_redirect):
    logout(request)
    return redirect(logout_redirect)


def register(request, register_temp, register_redirect):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, register_temp, {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            Merchant.objects.create(user=user)
            user.save()
            login(request, user)
            return redirect(register_redirect)

        except IntegrityError:
            return render(request, register_temp, {
                "message": "Username already taken."
            })

    return render(request, register_temp)
