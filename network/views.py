from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post

# Function that paginates the posts
def paginate(request, posts):
    paginated = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginated.get_page(page_number)
    return page_obj

# Function for posting Posts and saving them
def comment(request, user):
    post_content = request.POST["newpost"]
    # If post isnt empty, save it
    if post_content:
        new_post = Post(
            poster=user,
            content=post_content
        )
        new_post.save()

# Function for liking/disliking Posts
def like(request, user):
    post_id = json.loads(request.body)["post_id"]
    post = Post.objects.get(id=post_id)
    like = bool()

    # Post owner cant like their own posts
    if post.poster != user:

        # If the post is already liked, dislike it
        if post.user_set.all():
            user.likes.remove(post)
            post.likes -= 1
            post.save()
            like = False

        # If it isnt, like it
        else:
            user.likes.add(post)
            post.likes += 1
            post.save()
            like = True

        # Return the final number of likes on the post and status (dislike or like)
        return(post.likes, like)


def index(request):
    user = request.user
    if user.is_authenticated:
        # Posting posts in done in POST method
        if request.method == "POST":
            comment(request, user)

        # Liking and editing posts is done in PUT method
        if request.method == "PUT":
            # If the user is editing
            try: 
                content = json.loads(request.body)["post_content"]
                post_id = json.loads(request.body)["post_id"]
                post = Post.objects.get(pk=post_id)
                # User can edit only if he owns the post
                if user == post.poster:
                    # If contents of the posts are changed, then save them
                    if content != post.content:
                        post.content = content
                        post.save()
                        return JsonResponse({
                            "content": content,
                            "success": True
                        })
                    # If they arent do nothing
                    else:
                        return JsonResponse({
                            "success": False
                        })

            # If the user is liking the post
            except KeyError:
                postlikes, liked = like(request, user)

                return JsonResponse({
                    "likescount": postlikes,
                    "like": liked
                })

    posts = paginate(request, Post.objects.all().order_by("-timestamp"))

    return render(request, "network/index.html", {
        "posts": posts
    })

# View for showing followed accounts and their posts
def following(request):
    user = request.user
    if user.is_authenticated:
        # Users can still post on this page
        if request.method == "POST":
            comment(request, user)
        # If user is liking a post
        if request.method == "PUT":
            postlikes, liked = like(request, user)

            return JsonResponse({
                "likescount": postlikes,
                "like": liked
            })

        posts = paginate(request, Post.objects.filter(
            poster__in=user.following()).order_by("-timestamp"))

        # Rendering the same template, only posts are narrowed
        return render(request, "network/index.html", {
            "posts": posts
        })

    # If the user isnt logged in, they cant see this page so they get error
    else:
        return render(request, "network/error.html", {
            "error": "Error: Log in to view this page"
        })

# View for profiles
def profile(request, profile_id):
    user = request.user
    profile = User.objects.get(pk=profile_id)
    posts = paginate(request, Post.objects.filter(poster=profile).order_by("-timestamp"))

    # Determine if the profile is followed by the current user visiting it
    is_followed = True if user in profile.followers.all() else False
    # Number of followers the profile has
    following = User.objects.filter(followers=profile).count()

    if user.is_authenticated:
        # The owner of the profile can edit his posts
        if user == profile:
            if request.method == "PUT":
                content = json.loads(request.body)["post_content"]
                post_id = json.loads(request.body)["post_id"]
                post = Post.objects.get(pk=post_id)

                if content != post.content:
                    post.content = content
                    post.save()
                    return JsonResponse({
                        "content": content,
                        "success": True
                    })
                else:
                    return JsonResponse({
                        "success": False
                    })
        # And others may only like posts or follow the profile
        else:
            if request.method == "PUT":
                # Try to like a post
                if request.body:

                    postlikes, liked = like(request, user)

                    return JsonResponse({
                        "likescount": postlikes,
                        "like": liked
                    })
                # Else follow/unfollow
                else:
                    if is_followed:
                        profile.followers.remove(user)

                        return JsonResponse({
                            "follow": "Follow",
                            "followers": profile.followers.count(),
                            "following": following
                        })
                    else:
                        profile.followers.add(user)

                        return JsonResponse({
                            "follow": "Unfollow",
                            "followers": profile.followers.count(),
                            "following": following
                        })

    return render(request, "network/profile.html", {
        "profile": profile,
        "posts": posts,
        "is_followed": is_followed,
        "following": following
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
        if username:
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
    
    return render(request, "network/register.html")
