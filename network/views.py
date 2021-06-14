import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.core.paginator import Paginator
from itertools import chain


def index(request):
    #The boolean to determine whether accessed to following or index
    #since using the same template to help change header and title
    following_index = False

    posts = Post.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cur_page = 1
    if page_number != None:
        cur_page = int(page_number)

    last_page = int(paginator.num_pages)
    range = times(cur_page, last_page)
    see_last = True
    

    if (cur_page < last_page - 2):
        see_last = False   

    return render(request, "network/index.html", {
        "posts": page_obj,
        "range": range,
        "cur_page": cur_page,
        "last_page": last_page,
        "see_last": see_last,
        "following_index": following_index,
        "user": request.user
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


@login_required
def post(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    content = data.get("content", "")


    if not len(content) > 0:
        return JsonResponse({"error": "Invalid post."}, status=400)

    else:
        posted = Post.objects.create(
            user=request.user,
            content=content
        )
        posted.save()

    return JsonResponse({"message": "Successfully posted."}, status=201)


def profile(request, username):

    profile_owner = User.objects.get(username=username)
    following = Follow.objects.filter(followee= profile_owner)
    follower = None

    is_following = False
     
    if Follow.objects.filter(following=profile_owner).exists():

        follower = Follow.objects.get(following=profile_owner).followee.all()

        if request.user in follower:
            is_following = True

    

    


    posts = Post.objects.filter(
                    user = User.objects.get(username=profile_owner.username
                    )).order_by('id').reverse()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cur_page = 1
    if page_number != None:
        cur_page = int(page_number)

    last_page = int(paginator.num_pages)
    range = times(cur_page, last_page)
    see_last = True
    

    if (cur_page < last_page - 2):
        see_last = False
    
    if request.user.is_authenticated and request.user == profile_owner:        
        is_owner = True

    else:
        is_owner = False

    return render(request, "network/profile.html",{
        "profile_owner": profile_owner,
        "follower": follower,
        "following": following,
        "posts": page_obj,
        "is_owner": is_owner,
        "is_following": is_following,
        "range": range,
        "cur_page": cur_page,
        "last_page": last_page,
        "see_last": see_last
    })

def follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    profile_name = data.get("profile_name", "")

    print(f'The name of {profile_name}')

    followed = User.objects.get(username=profile_name)
    followee = User.objects.get(username=request.user.username)

    
    if Follow.objects.filter(following = followed).exists():
        being_followed = Follow.objects.get(following = followed)

        if followee in being_followed.followee.all():
            being_followed.followee.remove(followee)
            return JsonResponse({"message": "Unfollowed."}, status=201)
        else:
            being_followed.followee.add(followee)

            return JsonResponse({"message": "Followed."}, status=201)
    else:
        follow = Follow(following = followed)
        follow.save()
        follow.followee.add(followee)

        return JsonResponse({"message": "Followed."}, status=201)


def following_page(request):

    #The boolean to determine whether accessed from following or index
    #to help change header and title since this two methods use the
    #same template
    following_index = True
    posts = Post.objects.none()
    if request.user.is_authenticated:
        followings = Follow.objects.filter(followee= request.user)
        for following in followings:
            cur_follow = following.following
            post = Post.objects.filter(user=cur_follow)
            posts = posts.union(post)

        posts = posts.order_by('id').reverse()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        cur_page = 1
        if page_number != None:
            cur_page = int(page_number)

        last_page = int(paginator.num_pages)
        range = times(cur_page, last_page)
        see_last = True


        if (cur_page < last_page - 2):
            see_last = False

        

        return render(request, "network/index.html", {
            "posts": page_obj,
            "range": range,
            "cur_page": cur_page,
            "last_page": last_page,
            "see_last": see_last,
            "following_index": following_index,
            "user": request.user
        })

    else:
        return render(request, "network/login.html", {
                "message": "Sign in to access this feature"
            })

@login_required
def edit(request):
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    index = int(data.get("index", ""))
    content = data.get("content", "")
    if not len(content) > 0:
        return JsonResponse({"error": "Invalid edit."}, status=400)
    else:
        edited = Post.objects.get(pk=index)
        edited.content = content
        edited.save()
        return JsonResponse({"message": "Successfully edited"}, status=201)

@login_required
def like(request):
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    index = int(data.get("index", ""))
    
    liked_post = Post.objects.get(pk=index)
    
    if Like.objects.filter(
        liked_post=liked_post).exists():
        being_liked = Like.objects.get(liked_post=liked_post)
        if request.user in being_liked.liked_by.all():
            being_liked.liked_by.remove(request.user)
            return JsonResponse({"message": "Unliked post."}, status=201)
        else:
            being_liked.liked_by.add(request.user)
            return JsonResponse({"message": "Liked post."}, status=201)
    else:
        being_liked = Like(liked_post=liked_post)
        being_liked.save()
        being_liked.liked_by.add(request.user)
        return JsonResponse({"message": "Liked post."}, status=201)


@login_required
def comment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post_id = int(data.get("post_id", ""))
    content = data.get("content", "")
    re_comment = data.get("re_comment", )
    if not len(content) > 0:
        return JsonResponse({"error": "Invalid comment."}, status=400)
    else:
        if re_comment:
            linked_comment_id = int(data.get("comment_id", ""))
            linked_comment = Comment.objects.get(pk=linked_comment_id)
            comment = Comment.objects.create(
                content = content,
                posted_by = request.user,
                linked_post = Post.objects.get(pk=post_id),
                linked_comment = linked_comment
            )
            comment.save()
            return JsonResponse({"message": "Successfully commented"}, status=201)
        else:
            comment = Comment.objects.create(
                content = content,
                posted_by = request.user,
                linked_post = Post.objects.get(pk=post_id)
            )
            comment.save()
            return JsonResponse({"message": "Successfully commented"}, status=201)

def follow_page(request, username, follow):
        is_owner = False
        profile_owner = User.objects.get(username=username)
        followers = ''
        followings = ''
        
        if request.user.username == username:
            is_owner = True
        if follow == "follower":
            if Follow.objects.filter(following=profile_owner).exists():
                followers = Follow.objects.get(following=profile_owner).followee.all()
        elif follow == "following":
            followings = Follow.objects.filter(followee=profile_owner)

        return render(request, "network/follow.html", {
            "is_owner": is_owner,
            "followers": followers,
            "followings": followings,
            "follow": follow,
            "profile_owner": profile_owner
        })

                
    


# Helper function for pagination, so it can dynamically display 
# redirect button for 5 pages. i.e. If total 10 pages, and current page
# is 4, will return range(2, 7) so user can redirect to page 2-6,
# if current page is 10, will return (6,11), so user can redirect to
# page 6-10 ...
#
# @param cur_page the current page the user on
# @param last_page the last page for objects
# @return range of pages
def times(cur_page, last_page):
    if (last_page <= 5):
        return range(1, last_page+1)
    elif (cur_page <= 3):
        return range(1, 6)
    elif (cur_page >= last_page - 2):
        return range(last_page - 4, last_page+1)
    else:
        return range(cur_page-2, cur_page+3)

    

    

    