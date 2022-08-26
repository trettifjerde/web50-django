import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse

from web50.settings import MY_APPS
from commerce.models import Merchant

def index(request):
    projects = [{"name": name, "url": f'{name}:index'} for name in MY_APPS]
    return render(request, "home/home.html", {'projects': projects})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            else:
                return redirect('home:index')
        else:
            return render(request, 'home/login.html', {
                "message": "Invalid username and/or password."
            })
            
    elif request.method == 'GET' and 'next' in request.GET:
        try:
            project = request.GET.get('next').split('/')[1]
            return render(request, 'home/login.html', {'project': project})
        except:
            pass
    return render(request, 'home/login.html')

def logout_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logout(request)
        return JsonResponse({}, status=200)
    return redirect('home:index')

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, 'home/register.html', {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)

            if 'next' in request.POST:
                return redirect(request.POST['next'])
            else:
                return redirect('home:index')

        except IntegrityError:
            return render(request, 'home/register.html', {
                "message": "Username already taken."
            })
            
    elif request.method == "GET" and 'next' in request.GET:
        project = request.GET.get('next').split('/')[1]
        return render(request, 'home/register.html', {'project': project})

    return render(request, 'home/register.html')
