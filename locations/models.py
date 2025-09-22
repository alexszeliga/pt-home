from django.contrib.gis.db import models as locationModels
from django.contrib.gis.geos import Point
from django.db import models
from django.conf import settings

class Location(locationModels.Model):
    coords = locationModels.PointField(blank=True, null=True)

    def __str__(self):
        return f'lat: {self.coords.y}, lng: {self.coords.x}'

class UserLocation(Location):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)

    septa_locations = models.ManyToManyField('SeptaLocation', related_name='user_locations')
    
    def __str__(self):
        return f'{self.user.username} - {self.display_name}'

class SeptaLocation(Location):
    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    
    def __str__(self):
        return self.location_name