from django.db import models
from locations.models import Location
from django.conf import settings
from agency.models import Stop, Route

class UserLocation(Location):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255) 
    default_stop = models.ForeignKey(Stop,on_delete=models.SET_NULL,null=True,blank=True,related_name='default_stop')
    walking_distance = models.DecimalField(max_digits=10, decimal_places=2)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='user_location_route')

    def __str__(self):
        return f'{self.user.username} - {self.display_name}'
