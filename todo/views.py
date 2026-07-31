from django.shortcuts import render, redirect, get_object_or_404
from .models import Task



# Create your views here.


def home(request):
    if request.method == "POST":

        title = request.POST.get("title")

        if title:
            Task.objects.create(title=title)

        return redirect("home")
    
    tasks = Task.objects.all()
    
    context = {
        "title": "My Todo App",
        "tasks": tasks,
        
    }
    return render(request,"home.html", context)

def update_task(request, id):
    task = get_object_or_404(Task, id=id)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.completed = "completed" in request.POST
        task.save()

        return redirect("home")

    context = {
        "task": task,
    }

    return render(request, "update.html", context)

def delete_task(request, id):
    task = get_object_or_404(Task, id=id)

    task.delete()

    return redirect("home")