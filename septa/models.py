from django.db import models
from locations import models as locationModels

# Create your models here.
class SeptaLocation(locationModels.Location):
    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    
    def __str__(self):
        return self.location_name