import csv
import io
import requests
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.gis.geos import Point
from agency.models import Agency, Route, Stop, Calendar, CalendarDate, Trip, StopTime
from locations.models import Location
from agency.utils import reset_primary_key_sequence

GTFS_URL = "https://www3.septa.org/developer/gtfs_public.zip"
INNER_ZIP_FILENAME = "google_bus.zip"

class Command(BaseCommand):
    help = 'Downloads and imports the latest SEPTA GTFS data into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting SEPTA GTFS data import...'))
        
        try:
            self.stdout.write(f"Downloading data from {GTFS_URL}...")
            response = requests.get(GTFS_URL)
            response.raise_for_status()
            self.stdout.write("Download complete.")

            self.stdout.write("Opening outer zip file...")
            outer_zip = zipfile.ZipFile(io.BytesIO(response.content))

            self.stdout.write(f"Extracting inner '{INNER_ZIP_FILENAME}'...")
            inner_zip_bytes = outer_zip.read(INNER_ZIP_FILENAME)
            
            zip_file = zipfile.ZipFile(io.BytesIO(inner_zip_bytes))

            with transaction.atomic():
                self.stdout.write("Database transaction started. Deleting old data...")
                reset_primary_key_sequence(StopTime)
                reset_primary_key_sequence(Trip)
                reset_primary_key_sequence(CalendarDate)
                reset_primary_key_sequence(Calendar)
                reset_primary_key_sequence(Stop)
                reset_primary_key_sequence(Route)
                reset_primary_key_sequence(Agency)
                reset_primary_key_sequence(Location)
                self.stdout.write("Old data cleared.")

                self._import_agencies(zip_file)
                self._import_routes(zip_file)
                self._import_stops(zip_file)
                self._import_calendars(zip_file)
                self._import_calendar_dates(zip_file)
                self._import_trips(zip_file)
                self._import_stop_times(zip_file)

            self.stdout.write(self.style.SUCCESS('Successfully imported all SEPTA GTFS data.'))

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Error downloading GTFS file: {e}"))
        except KeyError:
            self.stderr.write(self.style.ERROR(f"Could not find '{INNER_ZIP_FILENAME}' inside the downloaded archive."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
            
    def _read_gtfs_file(self, zip_file, filename):
        """Helper to read a file from the zip archive and return a CSV reader."""
        with zip_file.open(filename) as f:
            reader = io.TextIOWrapper(f, encoding='utf-8-sig')
            return list(csv.DictReader(reader))

    def _import_agencies(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'agency.txt')
        agencies = [
            Agency(
                agency_id=row['agency_id'],
                agency_name=row['agency_name'],
                agency_url=row['agency_url'],
                agency_timezone=row['agency_timezone'],
                agency_lang=row.get('agency_lang'),
                agency_phone=row.get('agency_phone')
            ) for row in data
        ]
        Agency.objects.bulk_create(agencies)
        self.stdout.write(f"Imported {len(agencies)} agencies.")

    def _import_routes(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'routes.txt')
        agencies = {a.agency_id: a for a in Agency.objects.all()}
        routes = [
            Route(
                route_id=row['route_id'],
                agency=agencies.get(row.get('agency_id')),
                route_short_name=row['route_short_name'],
                route_long_name=row['route_long_name'],
                route_desc=row.get('route_desc', ''),
                route_type=int(row['route_type']),
                route_color=row.get('route_color', ''),
                route_text_color=row.get('route_text_color', '')
            ) for row in data
        ]
        Route.objects.bulk_create(routes)
        self.stdout.write(f"Imported {len(routes)} routes.")

    def _import_stops(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'stops.txt')
        stops = []
        for row in data:
            point = Point(float(row['stop_lon']), float(row['stop_lat']))
            stop = Stop(
                stop_id=row['stop_id'],
                stop_name=row['stop_name'],
                stop_code=row.get('stop_code'),
                stop_desc=row.get('stop_desc'),
                coords=point,
                zone_id=row.get('zone_id'),
                stop_url=row.get('stop_url'),
                location_type=int(row.get('location_type') or 0),
                parent_station_id=row.get('parent_station') or None
            )
            stops.append(stop)
        if stops:
            try:
                self.stdout.write(f"Importing or updating {len(stops)} stops")
                with transaction.atomic():
                    for s in stops:
                        s.save()
            except:
                self.stderr.write("Unable to save stops")
        # Stop.objects.bulk_create(stops, batch_size=500)
        self.stdout.write(f"Imported {len(stops)} stops.")

    def _import_calendars(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'calendar.txt')
        calendars = [
            Calendar(
                service_id=row['service_id'],
                monday=bool(int(row['monday'])),
                tuesday=bool(int(row['tuesday'])),
                wednesday=bool(int(row['wednesday'])),
                thursday=bool(int(row['thursday'])),
                friday=bool(int(row['friday'])),
                saturday=bool(int(row['saturday'])),
                sunday=bool(int(row['sunday'])),
                start_date=datetime.strptime(row['start_date'], '%Y%m%d').date(),
                end_date=datetime.strptime(row['end_date'], '%Y%m%d').date()
            ) for row in data
        ]
        Calendar.objects.bulk_create(calendars)
        self.stdout.write(f"Imported {len(calendars)} calendar services.")
        
    def _import_calendar_dates(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'calendar_dates.txt')
        dates = [
            CalendarDate(
                service_id=row['service_id'],
                date=datetime.strptime(row['date'], '%Y%m%d').date(),
                exception_type=int(row['exception_type'])
            ) for row in data
        ]
        CalendarDate.objects.bulk_create(dates, batch_size=500)
        self.stdout.write(f"Imported {len(dates)} calendar dates (exceptions).")

    def _import_trips(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'trips.txt')
        routes = {r.route_id: r for r in Route.objects.all()}
        trips = [
            Trip(
                trip_id=row['trip_id'],
                route=routes[row['route_id']],
                service_id=row['service_id'],
                trip_headsign=row.get('trip_headsign', ''),
                direction_id=int(row['direction_id']) if row.get('direction_id') else None,
                shape_id=row.get('shape_id')
            ) for row in data
        ]
        Trip.objects.bulk_create(trips, batch_size=500)
        self.stdout.write(f"Imported {len(trips)} trips.")

    def _import_stop_times(self, zip_file):
        data = self._read_gtfs_file(zip_file, 'stop_times.txt')
        trips = {t.trip_id: t for t in Trip.objects.all()}
        stops = {s.stop_id: s for s in Stop.objects.all()}
        
        stop_times = []
        for i, row in enumerate(data):
            trip = trips.get(row['trip_id'])
            stop = stops.get(row['stop_id'])
            
            if not trip or not stop:
                continue

            stop_times.append(
                StopTime(
                    trip=trip,
                    stop=stop,
                    arrival_time=row['arrival_time'],
                    departure_time=row['departure_time'],
                    stop_sequence=int(row['stop_sequence']),
                    stop_headsign=row.get('stop_headsign'),
                    pickup_type=int(row.get('pickup_type') or 0),
                    drop_off_type=int(row.get('drop_off_type') or 0)
                )
            )
            if i > 0 and i % 50000 == 0:
                self.stdout.write(f"  .. prepared {i} stop times")

        self.stdout.write("All stop times prepared. Starting bulk import...")
        StopTime.objects.bulk_create(stop_times, batch_size=500)
        self.stdout.write(f"Imported {len(stop_times)} stop times.")
