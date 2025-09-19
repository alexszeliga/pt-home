from django import forms

class LocationForm(forms.Form):
    name = forms.CharField(max_length=255,required=False)
    address = forms.CharField(max_length=255)
    place_id = forms.CharField(max_length=255)
    latitude = forms.DecimalField(max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6)
    display_name = forms.CharField(max_length=255,widget=forms.HiddenInput())
