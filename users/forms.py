from django import forms
from django.contrib.gis.geos import Point
from agency.models import Stop, Route
from users.models import UserLocation

from django.core.exceptions import ValidationError

class LocationForm(forms.Form):
    walking_choices = [
        ('0.1', '1/10 miles (about a block)'),
        ('0.25', '1/4 mile (2.5 blocks)'),
        ('0.5', 'Half mile (~5 blocks)'),
        ('1', '1 mile (~9 blocks)'),
    ]
    name = forms.CharField(max_length=255,required=False)
    walking_distance = forms.ChoiceField(choices=walking_choices,initial='0.25')
    address = forms.CharField(max_length=255,widget=forms.HiddenInput())
    place_id = forms.CharField(max_length=255,widget=forms.HiddenInput())
    latitude = forms.DecimalField(max_digits=9, decimal_places=6,widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9, decimal_places=6,widget=forms.HiddenInput())
    display_name = forms.CharField(max_length=255,widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
    
    def clean(self):
        
        cleaned_data = super().clean()
        lng = float(cleaned_data.get('longitude','0.0'))
        lat = float(cleaned_data.get('latitude', '0.0'))
        point = Point(lng,lat)

        if UserLocation.objects.filter(user=self.user,coords=point).exists():
            raise ValidationError('The selected location already exists')

        return cleaned_data

class DefaultSeptaLocationForm(forms.Form):
    default_septa_location = forms.ModelChoiceField(Stop.objects.none(), required=False)
    walking_choices = [
        ('0.10', '1/10 miles (about a block)'),
        ('0.25', '1/4 mile (2.5 blocks)'),
        ('0.50', 'Half mile (~5 blocks)'),
        ('1.00', '1 mile (~9 blocks)'),
    ]
    walking_distance = forms.ChoiceField(choices=walking_choices)
    route = forms.ModelChoiceField(Route.objects.none(), required=False)
    def __init__(self, *args, **kwargs):
        self.stop_queryset = kwargs.pop('stop_queryset', None) 
        self.route_queryset = kwargs.pop('route_queryset', None)
        self.walking_distance_initial = kwargs.pop('walking_distance_initial', None)
        super().__init__(*args, **kwargs)
        self.fields['default_septa_location'].queryset = self.stop_queryset 
        self.fields['route'].queryset = self.route_queryset
        self.fields['walking_distance'].initial = self.walking_distance_initial
