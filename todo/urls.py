from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("update/<int:id>/", views.update_task, name="update_task"),
    path("delete/<int:id>/", views.delete_task, name="delete_task"),
]