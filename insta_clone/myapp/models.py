# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models

from django.db import models

import uuid

#create a model for user
class UserModel(models.Model):
    #email field
    email = models.EmailField();
    #username field
    username = models.CharField(max_length=120)
    #password field
    password = models.CharField(max_length=40)
    #created on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated on field
    updated_on = models.DateTimeField(auto_now=True)

#create a model for session token
class SessionToken(models.Model):
    #user field
	user = models.ForeignKey(UserModel)
    # session-token field
	session_token = models.CharField(max_length=255)
    # last-request-on field
	last_request_on = models.DateTimeField(auto_now=True)
    # created-on field
	created_on = models.DateTimeField(auto_now_add=True)
    # is-valid field
	is_valid = models.BooleanField(default=True)

    # function to generate a session token
	def create_token(self):
        # generating session token
		self.session_token = uuid.uuid4()

# Create a model for post
class PostModel(models.Model):
  #user field
  user = models.ForeignKey(UserModel)
  #image field
  image = models.FileField(upload_to='user_images')
  #image-url field
  image_url = models.CharField(max_length=255)
  #caption field
  caption = models.CharField(max_length=240)
  #created-on field
  created_on = models.DateTimeField(auto_now_add=True)
  #updated -on field
  updated_on = models.DateTimeField(auto_now=True)
  has_liked = False

  @property
  def like_count(self):
      return len(LikeModel.objects.filter(post=self))

  @property
  def comments(self):
      return CommentModel.objects.filter(post=self).order_by('-created_on')

#create a model for liking a post
class LikeModel(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #post field
    post = models.ForeignKey(PostModel)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated-on field
    updated_on = models.DateTimeField(auto_now=True)

#create a model for adding a comment
class CommentModel(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #post field
    post = models.ForeignKey(PostModel)
    #comment text field


    comment_text = models.CharField(max_length=555)
    #upvote num field
    upvote_num = models.IntegerField(default=0)
    #created on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated on field
    updated_on = models.DateTimeField(auto_now=True)
