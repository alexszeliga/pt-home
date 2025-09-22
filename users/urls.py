from django.contrib import auth
from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/location/', views.location, name='user.add.location'),
    path('profile/location/<int:user_location_id>/', views.location_single, name='user.location'),
    path('profile/location/<int:user_location_id>/delete/', views.location_single_delete, name='user.location.delete'),
    path('profile/locations/', views.locations, name='user.locations'),
]
