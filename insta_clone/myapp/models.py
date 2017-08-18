# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
from django.db import models
# Create your models here.
from django.db import models

class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=120)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class SessionToken(models.Model):
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    def create_token(self):
        self.session_token = uuid.uuid4()

class PostModel(models.Model):
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to='user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    has_liked = False
    current_user = None
    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))
    @property
    def comments(self):
        comment_model = CommentModel.objects.filter(post=self).order_by('-votes')
        for model in comment_model:
            model.has_comment_liked = CommentLikeModel.objects.filter(user=self.current_user,comment_id=model.id).first()
        return comment_model


class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class CommentModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=555)
    votes = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    has_comment_liked = False
    @property
    def like_count(self):
        return len(CommentLikeModel.objects.filter(comment=self))

class CommentLikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    comment = models.ForeignKey(CommentModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class BrandModel(models.Model):
    name = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class PointsModel(models.Model):
    user = models.ForeignKey(UserModel)
    brand = models.ForeignKey(BrandModel)
    points = models.IntegerField(default=1)
    total_points = 0
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)