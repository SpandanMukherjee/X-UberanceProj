from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
