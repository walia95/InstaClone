# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, CommentLikeForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel, BrandModel, PointsModel, \
    CommentLikeModel
from django.contrib.auth.hashers import make_password, check_password
from imgurpython import ImgurClient
from clarifai.rest import ClarifaiApp
from insta_clone.settings import BASE_DIR

Client_ID = "d07cdb69eac824b"
Client_secret = "33369dc3b68df339cb1e2ddbbc984783957d9fc0"
Clarifai_key = "d9cdd283a5754aef87ed239a4b47b876"



def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            return render(request, "index.html", {"form": form, "error": "Id Created"})
        else:
            return render(request, "index.html", {"form": form, "error": "Invalid data"})
    elif request.method == "GET":
        form = SignUpForm()
        return render(request, "index.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = UserModel.objects.filter(username=username).first()
            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect("/feed/")
                    response.set_cookie(key="session_token", value=token.session_token)
                    return response
                else:
                    return render(request, "login.html", {"form": form, "error": "Invalid password"})
            else:
                return render(request, "login.html", {"form": form, "error": "Invalid username"})
    elif request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})


def check_validation(request):
    if request.COOKIES.get("session_token"):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get("session_token")).first()
        if session.is_valid:
            return session.user


def post_view(request):
    user = check_validation(request)
    if user:
        if request.method == 'GET':
            form = PostForm()
            return render(request, 'post.html', {'form': form, 'user': user})
        elif request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                path = str(BASE_DIR + "/user_images/" + post.image.url)
                post.save()
                try:
                    client = ImgurClient(Client_ID, Client_secret)
                    post.image_url = client.upload_from_path(path, anon=True)['link']
                    post.save()
                except:
                    print "Unable to connect to internet"
                    post.delete()
                    return render(request, 'post.html',
                                  {'form': form, 'user': user, 'error': "Internet Connectivity Issue"})
                points = win_points(user, post.image_url, caption)
                return render(request, 'post.html', {'form': form, 'user': user, 'error': points})
            else:
                return render(request, 'post.html', {'form': form, 'user': user, 'error': "Unable to Add Post"})

    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            post.current_user = user
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts, 'user': user})
    else:
        return redirect('/login/')


def self_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.filter(user=user).order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts, 'user': user})
    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                subject = "InstaClone Like Notification"
                post = PostModel.objects.filter(id=post_id).first()
                creator = UserModel.objects.filter(id=post.user_id).first()
                message = "Hello %s \n%s (%s) liked your photo" % (creator.name, user.username, user.name)
                print creator.email
                send_email(str(creator.email), subject, message)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            subject = "InstaClone Comment Notification"
            post = PostModel.objects.filter(id=post_id).first()
            creator = UserModel.objects.filter(id=post.user_id).first()
            message = "Hello %s \n%s (%s) commented your photo\n%s " % (
            creator.name, user.username, user.name, comment_text)
            send_email(creator.email, subject, message)
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


def upvote_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentLikeForm(request.POST)
        if form.is_valid():
            comment_id = form.cleaned_data.get('comment').id
            existing_comment_like = CommentLikeModel.objects.filter(comment_id=comment_id, user=user).first()
            comment = CommentModel.objects.get(id=comment_id, user=user)
            print str(comment.votes)
            if not existing_comment_like:
                CommentLikeModel.objects.create(comment_id=comment_id, user=user)
                comment.votes += 1
            else:
                existing_comment_like.delete()
                comment.votes -= 1
            comment.save()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def logout_view(request):
    user = check_validation(request)
    if user:
        token = SessionToken.objects.get(session_token=request.COOKIES.get("session_token"))
        token.is_valid = False
        token.save()
    return redirect('/login/')


def win_points(user, image_url, caption):
    brands_in_caption = 0
    brand_selected = ""
    points = 0;
    brands = BrandModel.objects.all()

    for brand in brands:
        if caption.__contains__(brand.name):
            brand_selected = brand.name
            brands_in_caption += 1
    image_caption = verify_image(image_url)
    print image_caption
    if brands_in_caption == 1:
        points += 50
        if image_caption.__contains__(brand_selected):
            points += 50
    else:
        if image_caption != "":
            for brand in brands:
                if image_caption.__contains__(brand.name):
                    brand_selected = brand.name
                    points += 50
                    break
    if points >= 50:
        brand = BrandModel.objects.filter(name=brand_selected).first()
        PointsModel.objects.create(user=user, brand=brand)
        return "Post Added with 1 points"
    else:
        return "Post Added"


def verify_image(image_url):
    try:
        app = ClarifaiApp(api_key=Clarifai_key)
        model = app.models.get("logo")
        responce = model.predict_by_url(url=image_url)
        if responce["status"]["code"] == 10000:
            if responce["outputs"][0]["data"]:
                return responce["outputs"][0]["data"]["regions"][0]["data"]["concepts"][0]["name"].lower()
        return ""
    except:
        print "Unable to connect to internet"
        return ""


def points_view(request):
    user = check_validation(request)
    if user:
        points_model = PointsModel.objects.filter(user=user).order_by('-created_on')
        points_model.total_points = len(PointsModel.objects.filter(user=user))
        brands = BrandModel.objects.all()
        return render(request, 'points.html', {'points_model': points_model, 'brands': brands, 'user': user})
    else:
        return redirect('/login/')
