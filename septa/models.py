from django.db import models
from locations import models as locationModels

# Create your models here.
class SeptaLocation(locationModels.Location):
    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    
    def __str__(self):
        return self.location_name

class Route(models.Model):
    route_id = models.CharField(max_length=255, unique=True,db_index=True)
    route_short_name = models.CharField(max_length=255)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.CharField(max_length=255)
    route_type = models.CharField(max_length=255)

class StopTime(models.Model):
    trip_id = models.CharField(max_length=255)
    arrival_time = models.CharField(max_length=255)
    departure_time = models.CharField(max_length=255)
    stop_id = models.CharField(max_length=255)
    stop_sequence = models.CharField(max_length=255)
    stop_headsign = models.CharField(max_length=255)
    pickup_type = models.CharField(max_length=255)
    drop_off_type = models.CharField(max_length=255)
    shape_dist_traveled = models.CharField(max_length=255)
    timepoint = models.CharField(max_length=255)
