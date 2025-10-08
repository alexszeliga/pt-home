from django.db import models
from locations.models import Location

class Agency(models.Model):
    agency_id = models.CharField(max_length=100, primary_key=True)
    agency_name = models.CharField(max_length=255)
    agency_url = models.URLField()
    agency_timezone = models.CharField(max_length=100)
    agency_lang = models.CharField(max_length=10, blank=True, null=True)
    agency_phone = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.agency_name

class Route(models.Model):
    route_id = models.CharField(max_length=100, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    route_short_name = models.CharField(max_length=50)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.TextField(blank=True, null=True)
    route_type = models.IntegerField() # See GTFS spec for types
    route_url = models.URLField(blank=True, null=True)
    route_color = models.CharField(max_length=6, blank=True, null=True)
    route_text_color = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.route_short_name} ({self.route_long_name})"

class Stop(Location):
    stop_id = models.CharField(max_length=100, primary_key=True)
    stop_code = models.CharField(max_length=100, blank=True, null=True)
    stop_name = models.CharField(max_length=255)
    stop_desc = models.TextField(blank=True, null=True)
    zone_id = models.CharField(max_length=100, blank=True, null=True)
    stop_url = models.URLField(blank=True, null=True)
    location_type = models.IntegerField(default=0)
    parent_station = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.stop_name

class Calendar(models.Model):
    service_id = models.CharField(max_length=100, primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.service_id

class CalendarDate(models.Model):
    id = models.AutoField(primary_key=True) # Has no natural primary key
    service_id = models.CharField(max_length=100) # Not a FK, relates to Calendar.service_id
    date = models.DateField()
    exception_type = models.IntegerField() # 1 for added, 2 for removed

    class Meta:
        unique_together = ('service_id', 'date')

    def __str__(self):
        return f"{self.service_id} on {self.date}"

class Trip(models.Model):
    trip_id = models.CharField(max_length=100, primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    service_id = models.CharField(max_length=100) # Relates to Calendar.service_id
    trip_headsign = models.CharField(max_length=255, blank=True, null=True)
    direction_id = models.IntegerField(blank=True, null=True)
    block_id = models.CharField(max_length=100, blank=True, null=True)
    shape_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Trip {self.trip_id} on {self.route.route_short_name}"

class StopTime(models.Model):
    id = models.AutoField(primary_key=True) # Has no natural primary key
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    arrival_time = models.CharField(max_length=10)
    departure_time = models.CharField(max_length=10)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField()
    stop_headsign = models.CharField(max_length=255, blank=True, null=True)
    pickup_type = models.IntegerField(default=0)
    drop_off_type = models.IntegerField(default=0)

    class Meta:
        # Each stop can only be visited once per trip.
        unique_together = ('trip', 'stop_sequence')
        ordering = ['trip', 'stop_sequence']

    def __str__(self):
        return f"{self.stop.stop_name} @ {self.arrival_time} on {self.trip.trip_id}"

