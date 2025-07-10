from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('todos/', views.todos_view, name='todos'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('habits/', views.habits_view, name='habits'),
]
