from django.core.management.base import BaseCommand
import requests
import zipfile
import io
import csv
from septa.models import Route

class Command(BaseCommand):
    help = 'Attempt to download and parse routes from Septa'

    def handle(self, *args, **options):
        gtfs_url = "https://www3.septa.org/developer/gtfs_public.zip"
        bus_routes = []
        self.stdout.write(self.style.SUCCESS('Contacting Septa for Routes'))

        try:
            response = requests.get(gtfs_url)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as zf_outer:
                if 'google_bus.zip' not in zf_outer.namelist():
                    self.stderr.write(self.style.ERROR("zip file doesn't contain bus list"))
                    return []
                bus_zip_data = zf_outer.read('google_bus.zip')
                with zipfile.ZipFile(io.BytesIO(bus_zip_data)) as zf_inner:
                    if 'routes.txt' not in zf_inner.namelist():
                        self.stderr.write(self.style.ERROR("inner zip file doesn't contain route list"))
                        return []
                    with zf_inner.open('routes.txt', 'r') as f:
                        reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'))
                        count = 0
                        for row in reader:
                            if row.get('route_type') == '3':
                                count += 1
                                Route.objects.update_or_create(route_id=row.get('route_id'), defaults={
                                    'route_short_name': row.get('route_short_name'),
                                    'route_long_name': row.get('route_long_name'),
                                    'route_desc': row.get('route_desc'),
                                    'route_type': row.get('route_type'),
                                })
                return f"Bus Routes Parsed: {count}"
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"unable to downlod Septa GTFS file: {e}"))
            return []
        except zipfile.BadZipFile:
            self.stderr.write(self.style.ERROR(f"Septa GTFS zip file is invalid"))
            return []
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"unknown exception: {e}"))
            return []
        