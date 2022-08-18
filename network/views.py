import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Networker, NetworkPost

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def get_paginated_page(request, posts):
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page

def index(request):
    posts = NetworkPost.objects.all()
    page = get_paginated_page(request, posts)
    return render(request, "network/index.html", {
        'page': page,
        'header': 'All posts'
    })

def new(request):
    if request.method == 'POST':
        print(request.POST)
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.networker = Networker.objects.get(user=request.user)
            new_post.save()
    return redirect('network:index')

def user(request, user_id):
    networker = Networker.objects.get(user=user_id)
    posts = NetworkPost.objects.filter(networker=networker)
    page = get_paginated_page(request, posts)
    return render(request, "network/index.html", {
        "networker" : networker, 
        "header": f"{networker}'s posts",
        "page": page,
        "follows": False if not request.user.is_authenticated else networker.followers.contains(request.user.networker)
        })

def edit(request, post_id):
    if not is_ajax(request):
        return redirect('network:index')
    try:
        post = NetworkPost.objects.get(pk=post_id)

        if post.networker.user != request.user:
            return JsonResponse({'error': 'You have no rights to edit this post'})

        if request.method == 'GET':
            return JsonResponse({'text': post.text})

        if request.method == 'POST':
            data = json.loads(request.body)
            form = PostForm(data, instance=post)
            if form.is_valid():
                post = form.save()
                return JsonResponse({'post': post.serialize()})
            else:
                return JsonResponse({'errors': form.errors})
    except Exception as ex:
        print(ex)
        return JsonResponse({'error': str(ex)})

def follow(request, user_id):
    if not is_ajax(request):
        return redirect('network:user', user_id=user_id)

    if request.method == 'PUT':
        networker = Networker.objects.get(user=user_id)
        requester = Networker.objects.get(user=request.user)

        if networker.followers.contains(requester):
            networker.followers.remove(requester)
        else:
            networker.followers.add(requester)
        return JsonResponse({})

    return JsonResponse({'error': 'Must be PUT-request'})

@login_required
def following(request):
    follows = request.user.networker.follows.all()
    posts = NetworkPost.objects.filter(networker__in=follows)
    page = get_paginated_page(request, posts)

    return render(request, "network/index.html", {
        'page': page, 
        'hide_form': True,
        'header': f"{request.user}'s feed"
    })

@login_required
def like(request):
    if not is_ajax(request):
        return redirect('network:index')
    if request.method == 'PUT':
            networker = request.user.networker
            data = json.loads(request.body)
            post = NetworkPost.objects.get(pk=data["post_id"])
            if post.likes.contains(networker):
                post.likes.remove(networker)
            else:
                post.likes.add(networker)
            post.save()
            return JsonResponse({'likes': post.likes.count()}) 
        #except:
            #return JsonResponse({'error': 'Error reading request'})
    return JsonResponse({'error': 'Must be PUT-request'})
    
    