from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, SignupForm, TaskForm
from .models import Task

# Create your views here.

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
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
                messages.success(request, "You are now logged in.")
                return redirect("home")
    

    else:
        form = LoginForm()

    context = {
        "form": form,

    }
    return render(request, "login.html", context)

@login_required
@require_POST
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

@login_required
def home(request):
    task_form = TaskForm()

    if request.method == "POST":
        task_form = TaskForm(request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task added successfully.")
            return redirect("home")
        messages.error(request, "Please correct the errors below.")

    search = request.GET.get("search", "").strip()
    filter_status = request.GET.get("status", "")
    user_tasks = Task.objects.filter(user=request.user)
    total_tasks = user_tasks.count()
    pending_tasks = user_tasks.filter(completed=False).count()
    completed_tasks = user_tasks.filter(completed=True).count()
    tasks = user_tasks

    if search:
        tasks = tasks.filter(title__icontains=search)

    if filter_status == "completed":
        tasks = tasks.filter(completed=True)
    elif filter_status == "pending":
        tasks = tasks.filter(completed=False)

    context = {
        "title": "My Todo App",
        "tasks": tasks,
        "search": search,
        "status": filter_status,
        "task_form": task_form,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
    }

    return render(request, "home.html", context)

@login_required
def update_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect("home")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm(instance=task)

    return render(request, "update.html", {"task": task, "form": form})

@login_required
@require_http_methods(["GET", "POST"])
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("home")

    return render(request, "confirm_delete.html", {"task": task})

@login_required
@require_POST
def toggle_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.completed = not task.completed
    task.save()
    messages.success(request, "Task status updated.")
    return redirect("home")