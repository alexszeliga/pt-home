from django.db import models
from locations.models import Location
from django.conf import settings
from agency.models import Stop

class UserLocation(Location):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255) 
    stops = models.ManyToManyField(Stop, related_name='stops')
    default_stop = models.ForeignKey(Stop,on_delete=models.SET_NULL,null=True,blank=True,related_name='default_stop')

    def __str__(self):
        return f'{self.user.username} - {self.display_name}'
