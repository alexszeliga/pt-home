import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import render, redirect, get_object_or_404
from . import forms
from users.models import UserLocation
from agency.models import Stop

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
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
        form = forms.LocationForm(request.POST, user=request.user)
        if form.is_valid():

            point = Point(float(form.cleaned_data['longitude']), float(form.cleaned_data['latitude']))

            loc, _created = UserLocation.objects.get_or_create(coords=point, defaults={
                'user' : request.user,
                'display_name': form.cleaned_data['name'] or form.cleaned_data['display_name'],
            })

            distance = D(mi=float(form.cleaned_data['walking_distance']))

            stops = Stop.objects.filter(coords__dwithin=(point, distance))

            loc.stops.add(*stops)

            return redirect('user.locations')
        else:
            return render(request, 'users/location.html', {'user': request.user, 'form': form, 'api_key': os.getenv('GOOGLE_MAPS_PLACES_API_KEY')})
    form = forms.LocationForm(user=request.user)
    return render(request, 'users/location.html', {'user': request.user, 'form': form, 'api_key': os.getenv('GOOGLE_MAPS_PLACES_API_KEY')})

@login_required
def locations(request):
    user_locations = UserLocation.objects.filter(user=request.user).select_related('user', 'location_ptr')
    return render(request, 'users/locations.html', {'userLocations':user_locations})

@login_required
def location_single(request, user_location_id):
    user_locations = UserLocation.objects.filter(user=request.user).select_related('user', 'location_ptr')
    user_location = get_object_or_404(user_locations, pk=user_location_id)

    if request.method == "GET":
        form = forms.DefaultSeptaLocationForm(initial={'default_septa_location': user_location.default_stop},queryset=user_location.stops)
        return render(request, 'users/location_single.html', {'userLocation':user_location,'api_key': os.getenv('GOOGLE_MAPS_PLACES_API_KEY'), 'default_septa_location_form': form})

    if request.method == 'POST':
        form = forms.DefaultSeptaLocationForm(request.POST, queryset=user_location.stops)
        if form.is_valid():
            septaLocation = form.cleaned_data['default_septa_location']
            user_location.default_stop = septaLocation
            user_location.save()
    return render(request, 'users/location_single.html', {'userLocation':user_location,'api_key': os.getenv('GOOGLE_MAPS_PLACES_API_KEY'), 'default_septa_location_form': form})

@login_required
def location_single_delete(request, user_location_id):
    user_locations = UserLocation.objects.filter(user=request.user).select_related('user', 'location_ptr')
    user_location = get_object_or_404(user_locations, pk=user_location_id)
    user_location.delete()
    return redirect('user.locations')