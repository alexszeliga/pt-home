from django.contrib.gis.db import models as locationModels
from django.db import models
from django.conf import settings

class Location(locationModels.Model):
    name = locationModels.CharField(max_length=255)
    address = locationModels.CharField(max_length=255)
    location = locationModels.PointField(blank=True, null=True)
    place_id = locationModels.CharField(max_length=255, unique=True, db_index=True)

    users = locationModels.ManyToManyField(settings.AUTH_USER_MODEL, through='UserLocation', related_name='claimed_locations')

    def __str__(self):
        return self.name

class UserLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'location')
    
    def __str__(self):
        return f'{self.user.username} - {self.display_name}'