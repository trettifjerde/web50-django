import json
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse

from .models import Project, Pic
from web50.settings import MY_APPS

def getNext(request):
    request_data = request.POST if request.method == "POST" else request.GET
    if 'next' in request_data:
        project = request_data.get('next').split('/')[1]
        if project in MY_APPS:
            return project, request_data.get('next')
    return 'home', reverse('home:index')

def index(request):
    return render(request, "home/home.html", {'projects': Project.objects.filter(hidden=False).order_by('name')})

def login_view(request):
    project, go_to_next = getNext(request)
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(go_to_next)
        else:
            return render(request, 'home/login.html', {
                'project': project, 
                'next': go_to_next,
                'message': 'Invalid username or password'
            })
            
    return render(request, 'home/login.html', {'project': project, 'next': go_to_next})

def logout_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logout(request)
        return JsonResponse({}, status=200)
    return redirect('home:index')

def register_view(request):
    project, go_to_next = getNext(request)

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, 'home/register.html', {
                "message": "Passwords must match.",
                "project": project,
                "next": go_to_next
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)

            return redirect(go_to_next)

        except IntegrityError:
            return render(request, 'home/register.html', {
                "message": "Username already taken.",
                "project": project,
                "next": go_to_next
            })

    return render(request, 'home/register.html', {
                "project": project,
                "next": go_to_next
            })
