from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth import login, logout
from .forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required




# Create your views here.

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("home")
    else:
        form = SignupForm()

    context = {
        "form": form,
    }

    return render(request,"signup.html", context)

def login_user(request):
    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect("home")
    

    else:
        form = LoginForm()

    context = {
        "form": form,

    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)

    return redirect("home")
@login_required
def home(request):
    if request.method == "POST":

        title = request.POST.get("title")

        if title:
            Task.objects.create(
                title=title,
                user=request.user
                )

        return redirect("home")
    
    tasks = Task.objects.filter(user=request.user)
    
    context = {
        "title": "My Todo App",
        "tasks": tasks,
        
    }
    return render(request,"home.html", context)
@login_required
def update_task(request, id):
    task = get_object_or_404(
        Task, 
        id=id,
        user=request.user
        )

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.completed = "completed" in request.POST
        task.save()

        return redirect("home")

    context = {
        "task": task,
    }

    return render(request, "update.html", context)
@login_required
def delete_task(request, id):
    task = get_object_or_404(
        Task, 
        id=id,
        user=request.user
        )

    task.delete()

    return redirect("home")