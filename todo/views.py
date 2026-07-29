from django.shortcuts import render, redirect
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
