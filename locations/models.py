from django.contrib.gis.db import models as locationModels

class Location(locationModels.Model):
    coords = locationModels.PointField(blank=True, null=True)

    def __str__(self):
        return f'lat: {self.coords.y}, lng: {self.coords.x}'
