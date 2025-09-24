from django.db.models.signals import post_save
from django.contrib.gis.geos import Point
from django.dispatch import receiver, Signal
from users.models import UserLocation
from septa.models import SeptaLocation
import requests



# Define a custom signal that will pass the instance and form data
user_location_form_saved = Signal()

@receiver(user_location_form_saved, sender=UserLocation)
def location_created_handler(sender, instance: UserLocation, form, created, **kwargs):
    if created:
        septaResponse = requests.get(f"https://www3.septa.org/api/locations/get_locations.php?lat={instance.coords.y}&lon={instance.coords.x}&radius={form.cleaned_data['walking_distance']}")
        if septaResponse.status_code == 200:
            locations = septaResponse.json()
            for location in locations:
                lon = float(location['location_lon'])
                lat = float(location['location_lat'])
                name = location['location_name']
                location_type = location['location_type']
                location_id = location['location_id']
                point = Point(lon, lat)
                septaLocation, created = SeptaLocation.objects.get_or_create(coords=point, defaults={
                    'location_name':name, 
                    'location_type': location_type,
                    'location_id': location_id,
                })
                instance.septa_locations.add(septaLocation)
