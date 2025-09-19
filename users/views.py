import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.gis.geos import Point
from django.shortcuts import render, redirect
from . import forms
from locations.models import Location, UserLocation

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(type(form))
        if form.is_valid():
            form.save()
            return redirect('login') # Redirect to login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data('username')
            password = form.cleaned_data('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid Username or Password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
            

@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def location(request):
    if request.method == 'POST':
        form = forms.LocationForm(request.POST)
        if form.is_valid():

            point = Point(float(form.cleaned_data['longitude']), float(form.cleaned_data['latitude']))
            location, created = Location.objects.get_or_create(
                place_id=form.cleaned_data['place_id'],
                defaults={
                    'address': form.cleaned_data['address'],
                    'location': point,
                }
            )

            UserLocation.objects.create(
                user = request.user,
                location = location,
                display_name = form.cleaned_data['name'] or form.cleaned_data['display_name'],
            )

            return redirect('user.locations')
    form = forms.LocationForm()
    return render(request, 'users/location.html', {'user': request.user, 'form': form, 'api_key': os.getenv('GOOGLE_MAPS_PLACES_API_KEY')})

@login_required
def locations(request):
    user_locations = UserLocation.objects.filter(user=request.user).select_related('user', 'location')
    return render(request, 'users/locations.html', {'userLocations':user_locations})
