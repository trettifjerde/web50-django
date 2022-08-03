from django.shortcuts import render
from .settings import MY_APPS

def home(request):
    projects = [{"name": name, "url": f'{name}:index'} for name in MY_APPS]
    return render(request, "home.html", {'projects': projects})