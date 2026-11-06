from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .models import Task


class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username","email","password1","password2"]

class LoginForm(AuthenticationForm):
    pass


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "completed"]