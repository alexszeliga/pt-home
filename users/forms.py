from django import forms
from django.contrib.gis.geos import Point
from locations.models import Location, UserLocation
from django.core.exceptions import ValidationError

class LocationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

    name = forms.CharField(max_length=255,required=False)
    address = forms.CharField(max_length=255,widget=forms.HiddenInput())
    place_id = forms.CharField(max_length=255,widget=forms.HiddenInput())
    latitude = forms.DecimalField(max_digits=9, decimal_places=6,widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9, decimal_places=6,widget=forms.HiddenInput())
    display_name = forms.CharField(max_length=255,widget=forms.HiddenInput())

    def clean(self):
        
        cleaned_data = super().clean()
        lng = float(cleaned_data.get('longitude','0.0'))
        lat = float(cleaned_data.get('latitude', '0.0'))
        point = Point(lng,lat)

        if UserLocation.objects.filter(user=self.user,coords=point).exists():
            raise ValidationError('The selected location already exists')

        return cleaned_data
