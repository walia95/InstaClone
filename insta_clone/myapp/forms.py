from django import forms
from models import UserModel, PostModel, LikeModel, CommentModel

#create a sign-up form
class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields=['username',  'email', 'password' ]

#create a login-form
class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'password']

#create a post-form
class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image', 'caption']


#create a like-form
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

# create a comment-form
class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']


from django import forms
#create a upvote-form
class UpvoteForm(forms.Form):
    id = forms.IntegerField()
