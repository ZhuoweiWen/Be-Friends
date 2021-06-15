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

# The function for all post page
def index(request):
    # The boolean to determine whether accessed to following or index
    # since using the same template to help change header and title
    following_index = False

    # Get the post and set up paginator
    posts = Post.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Set cur_page to 1 so user redirect to page 1 as default 
    # and update it if necessary
    cur_page = 1
    if page_number != None:
        cur_page = int(page_number)

    # Get the last page and get the range of pages
    last_page = int(paginator.num_pages)
    range = times(cur_page, last_page)

    # Boolean whether last page is within the next two pages
    see_last = True
    
    # Update boolean if last page not within next two pages
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

# Function for handling add new post request
@login_required
def post(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Load data and content
    data = json.loads(request.body)
    content = data.get("content", "")


    # If empty post return error
    if not len(content) > 0:
        return JsonResponse({"error": "Invalid post."}, status=400)

    # Create a new post object
    else:
        posted = Post.objects.create(
            user=request.user,
            content=content
        )
        posted.save()

    return JsonResponse({"message": "Successfully posted."}, status=201)

# Function for profile page
def profile(request, username):

    # Get the profile owner
    profile_owner = User.objects.get(username=username)
    # Get all people the user is following
    following = Follow.objects.filter(followee= profile_owner)
    # Set follower to none by default
    follower = None

    # Boolean for whether request user is following profile owner
    is_following = False
      
    if Follow.objects.filter(following=profile_owner).exists():
        # Get the followers of the profile owner
        follower = Follow.objects.get(following=profile_owner).followee.all()
        # Check if request user following profile owner
        if request.user in follower:
            is_following = True

    

    

    # Get all the posts of profile owner
    posts = Post.objects.filter(
                    user = User.objects.get(username=profile_owner.username
                    )).order_by('id').reverse()

    # Set up paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # The current page the user is on
    cur_page = 1
    if page_number != None:
        cur_page = int(page_number)
    # Get the range of pages
    last_page = int(paginator.num_pages)
    range = times(cur_page, last_page)
    see_last = True
    
    # Check if last page within next two pages
    if (cur_page < last_page - 2):
        see_last = False
    
    # See if request user is owner of the profile
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

# Function for handling follow request
def follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Load data and get the profile owner the request user is trying to follow
    data = json.loads(request.body)
    profile_name = data.get("profile_name", "")

    # Get the follower and the user being followed
    followed = User.objects.get(username=profile_name)
    followee = User.objects.get(username=request.user.username)

    # If the user being followed already has a follow object
    if Follow.objects.filter(following = followed).exists():

        being_followed = Follow.objects.get(following = followed)

        # If request user already followed profile owner, remove request user
        if followee in being_followed.followee.all():
            being_followed.followee.remove(followee)
            return JsonResponse({"message": "Unfollowed."}, status=201)
        # If not following profile owner, add request user to the list
        else:
            being_followed.followee.add(followee)
            return JsonResponse({"message": "Followed."}, status=201)
    # If the request user is the first ever follower of profile owner
    else:
        # Create a new follow object
        follow = Follow(following = followed)
        follow.save()
        follow.followee.add(followee)

        return JsonResponse({"message": "Followed."}, status=201)

# Function for handling the following page
def following_page(request):

    #The boolean to determine whether accessed from following or index
    #to help change header and title since this two methods use the
    #same template
    following_index = True

    # Set post to none by default
    posts = Post.objects.none()

    # If user logged in
    if request.user.is_authenticated:
        # Get all followings of the user
        followings = Follow.objects.filter(followee= request.user)
        # Add posts of followings to posts list
        for following in followings:
            cur_follow = following.following
            post = Post.objects.filter(user=cur_follow)
            posts = posts.union(post)

        # Reverse post so newer post is presented first
        posts = posts.order_by('id').reverse()

        # Set up paginator
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


# The function for handling edit request
@login_required
def edit(request):
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)
    # Load data and get the post_id and content
    data = json.loads(request.body)
    index = int(data.get("index", ""))
    content = data.get("content", "")
    # Check whether edit is valid
    if not len(content) > 0:
        return JsonResponse({"error": "Invalid edit."}, status=400)
    else:
        # Update post
        edited = Post.objects.get(pk=index)
        edited.content = content
        edited.save()
        return JsonResponse({"message": "Successfully edited"}, status=201)


# Function for handling like feature
@login_required
def like(request):
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Load data and get post id
    data = json.loads(request.body)
    index = int(data.get("index", ""))
    
    liked_post = Post.objects.get(pk=index)
    
    # Check if like object already exists
    if Like.objects.filter(
        liked_post=liked_post).exists():
        # Get the like object
        being_liked = Like.objects.get(liked_post=liked_post)
        # If user already liked the post, remove the like
        if request.user in being_liked.liked_by.all():
            being_liked.liked_by.remove(request.user)
            return JsonResponse({"message": "Unliked post."}, status=201)
        # If user haven't like the post, update like
        else:
            being_liked.liked_by.add(request.user)
            return JsonResponse({"message": "Liked post."}, status=201)
    else:
        # If this is the first like of the post, create like object
        being_liked = Like(liked_post=liked_post)
        being_liked.save()
        being_liked.liked_by.add(request.user)
        return JsonResponse({"message": "Liked post."}, status=201)


# Function for comment feature
@login_required
def comment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get post_id and content of comment, and boolean whether this is replying comment
    data = json.loads(request.body)
    post_id = int(data.get("post_id", ""))
    content = data.get("content", "")
    re_comment = data.get("re_comment", )
    # Handle invalid comment
    if not len(content) > 0:
        return JsonResponse({"error": "Invalid comment."}, status=400)
    else:
        # If replying to comment
        if re_comment:
            # Get the comment the user is replying to
            linked_comment_id = int(data.get("comment_id", ""))
            linked_comment = Comment.objects.get(pk=linked_comment_id)

            # Create the comment object
            comment = Comment.objects.create(
                content = content,
                posted_by = request.user,
                linked_post = Post.objects.get(pk=post_id),
                linked_comment = linked_comment
            )
            comment.save()
            return JsonResponse({"message": "Successfully commented"}, status=201)
        # If new comment
        else:
            # Create new comment
            comment = Comment.objects.create(
                content = content,
                posted_by = request.user,
                linked_post = Post.objects.get(pk=post_id)
            )
            comment.save()
            return JsonResponse({"message": "Successfully commented"}, status=201)

# Function for follow_page which display the lists of user 
# the profile_owner is following or the list of followers of profile owner
def follow_page(request, username, follow):
        
        
        profile_owner = User.objects.get(username=username)
        followers = ''
        followings = ''

        # Check if request user is owner of the page
        is_owner = False
        if request.user.username == username:
            is_owner = True

        # If checking followers of profile owner
        if follow == "follower":
            # Get followers of profile owner
            if Follow.objects.filter(following=profile_owner).exists():
                followers = Follow.objects.get(following=profile_owner).followee.all()
        # If checking profile owner followings
        elif follow == "following":
            # Get followings of profile owner
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

    

    

    