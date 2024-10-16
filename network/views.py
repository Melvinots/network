from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    page_obj = paginate(1)
    return render(request, "network/index.html", {
        "posts": [post.serialize(request.user) for post in page_obj],
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
    })


def get_posts(request, page_number):
    if request.method == "GET":
        page_obj = paginate(page_number)
        return render(request, "network/index.html", {
            "posts": [post.serialize(request.user) for post in page_obj],
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        })
    return JsonResponse({"error": "GET request required."}, status=400)


def paginate(page_number):
    posts = Post.objects.all().order_by('-date_time')
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def edit_post(request, post_id):

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    if request.method == "GET":
        return JsonResponse([post.serialize(request.user)], safe=False)
    elif request.method == "PUT":

        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
            post.save()
            return HttpResponse(status=204)
        else:
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
            post.save()
            return JsonResponse({"likes": post.likes.count()}, safe=False) 
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(poster=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    return JsonResponse({"error": "POST request required."}, status=400)
    

def profile(request, username, page_number):
    try:
        profile = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    if request.method == "GET":
        posts = Post.objects.filter(poster=profile).order_by('-date_time')
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)

        return render(request, "network/profile.html", {
            "username": username,
            "posts": [post.serialize(request.user) for post in page_obj],
            "followers" : profile.followers.count(),
            "following": profile.following.count(),
            "is_following": request.user in profile.followers.all(),
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        })
    elif request.method == "PUT":
        user = request.user
        if request.user in profile.followers.all():
            text = "Follow"
            profile.followers.remove(user)
            user.following.remove(profile)
        else:
            text = "Unfollow"
            profile.followers.add(user)
            user.following.add(profile)
        profile.save()
        user.save()
        return JsonResponse({
            "followers": profile.followers.count(),
            "text": text
            }, safe=False)
    return JsonResponse({"error": "GET or PUT request required."}, status=400)
      
        
@login_required
def following(request, page_number):

    following = request.user.following.all()
    posts = Post.objects.filter(poster__in=following).order_by('-date_time')
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "posts": [post.serialize(request.user) for post in page_obj],
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
