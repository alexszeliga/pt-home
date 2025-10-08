from django.db.models.signals import post_save
from django.contrib.gis.geos import Point
from django.dispatch import receiver, Signal
from locations.models import Location
from users.models import UserLocation
from agency.models import Stop
import requests

# Define a custom signal that will pass the instance and form data
user_location_form_saved = Signal()

@receiver(user_location_form_saved, sender=UserLocation)
def location_created_handler(sender, instance: UserLocation, form, created, **kwargs):
    print('deprecated')