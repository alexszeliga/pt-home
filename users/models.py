from django.db import models
from locations.models import Location
from django.conf import settings
from septa.models import SeptaLocation

# Create your models here.

class UserLocation(Location):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)

    septa_locations = models.ManyToManyField(SeptaLocation, related_name='septa_locations')
    default_septa_location = models.ForeignKey(SeptaLocation,on_delete=models.SET_NULL,null=True,blank=True,related_name='default_septa_location')

    def __str__(self):
        return f'{self.user.username} - {self.display_name}'
