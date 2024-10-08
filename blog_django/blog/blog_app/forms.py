from django import forms

from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
