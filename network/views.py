import json
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from .forms import PostForm
from .models import Networker, NetworkPost

def ajax_required(redirect_url='network:index'):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return function(request, *args, **kwargs)
            else: 
                return redirect(redirect_url, **kwargs)
        return wrapper
    return decorator

def get_paginated_page(posts, page_number):
    paginator = Paginator(posts, 10)
    page = paginator.get_page(page_number)
    return page

def index(request):
    posts = NetworkPost.objects.all()
    page = get_paginated_page(posts, request.GET.get('page'))
    return render(request, "network/index.html", {
        'page': page,
        'header': 'All posts'
    })

@login_required
@ajax_required()
def new(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = PostForm(data)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.networker = Networker.objects.get(user=request.user)
            new_post.save()
            post = TemplateResponse(request, 'network/post.html', {'post': new_post, 'user': request.user})
            post.render()
            return JsonResponse({'post': post.content.decode()})
        else:
            return JsonResponse({'error': 'Form not valid'})
    else:
        return JsonResponse({'error': 'Not POST-request'})

def user(request, user_id):
    try:
        networker = Networker.objects.get(user=user_id)
        posts = NetworkPost.objects.filter(networker=networker)
        page = get_paginated_page(posts, request.GET.get('page'))
        return render(request, "network/index.html", {
            "networker" : networker, 
            "header": f"{networker}'s posts",
            "page": page,
            "follows": False if not request.user.is_authenticated else networker.followers.contains(request.user.networker)
            })
    except:
        raise Http404

@login_required
@ajax_required()
def get_post(request):
    if request.method == "GET":
        try:
            post = NetworkPost.objects.get(pk=request.GET.get('postId'))
            if request.user == post.networker.user:
                return JsonResponse({'text': post.text})
            else:
                return JsonResponse({'error': 'You have no rights to edit this post'})
        except Exception as ex:
            return JsonResponse({'error': str(ex)})
    else:
        return JsonResponse({'error': 'Must be GET request'})

@login_required
@ajax_required()
def edit_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post = NetworkPost.objects.get(pk=data['postId'])

            if post.networker.user != request.user:
                return JsonResponse({'error': 'You have no rights to edit this post'})

            old_post_text = post.text
            form = PostForm(data, instance=post)

            if form.is_valid():
                if form.cleaned_data['text'] == old_post_text:
                    return JsonResponse({'error': 'You have not changed anything'})

                post = form.save()
                return JsonResponse({'post': post.serialize()})
            else:
                return JsonResponse({'errors': form.errors})

        except Exception as ex:
            print(ex)
            return JsonResponse({'error': str(ex)})
    else:
        return JsonResponse({'error': 'Must be POST request'})

@login_required
@ajax_required()
def delete_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Must be a POST request'})
    
    try:
        data = json.loads(request.body)
        post = NetworkPost.objects.get(pk=data['postId'])

        if request.user != post.networker.user:
            return JsonResponse({'error': 'You have no rights to delete this post'})

        post.delete()

        return JsonResponse({'ok': ''})
        
    except Exception as ex:
        return JsonResponse({'error': str(ex)})

@login_required
@ajax_required('network:user')
def follow(request):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Must be PUT-request'})

    networker = Networker.objects.get(user=json.loads(request.body)['userId'])
    requester = Networker.objects.get(user=request.user)

    if requester == networker:
        return JsonResponse({'error': 'You cannot follow yourself'})

    button_text = ''

    if networker.followers.contains(requester):
        networker.followers.remove(requester)
        button_text = 'Follow'
    else:
        networker.followers.add(requester)
        button_text = 'Unfollow'

    return JsonResponse({'text': button_text, 'followers': networker.followers.count()})


@login_required
def feed(request):
    follows = request.user.networker.follows.all()
    posts = NetworkPost.objects.filter(networker__in=follows)
    page = get_paginated_page(posts, request.GET.get('page'))

    return render(request, "network/index.html", {
        'page': page, 
        'hide_form': True,
        'header': f"{request.user}'s feed"
    })

@login_required
@ajax_required()
def like(request):
    if request.method == 'PUT':
        try:
            networker = request.user.networker
            data = json.loads(request.body)
            post = NetworkPost.objects.get(pk=data["post_id"])
            if post.likes.contains(networker):
                post.likes.remove(networker)
            else:
                post.likes.add(networker)
            post.save()
            return JsonResponse({'likes': post.likes.count()}) 
        except:
            return JsonResponse({'error': 'Error reading request'})
    return JsonResponse({'error': 'Must be PUT-request'})

@login_required
@ajax_required()
def avatar(request):    
    if request.method == 'POST':
            new_file = BytesIO(request.body)
            request.user.networker.save_image(new_file)
            return JsonResponse({}, status=200)
    else:
        return JsonResponse({'error': 'Bad Request'}, status=400)

@login_required
@ajax_required()
def delete_avatar(request):
    if request.method == 'PUT':
        request.user.networker.delete_image()
        return JsonResponse({}, status=200)
    else:
        return JsonResponse({'error': 'Bad Request'}, status=400)

    
    