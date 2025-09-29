from django.core.management.base import BaseCommand
from django.db.models import Model
from zipfile import ZipFile
from csv import DictReader
from io import TextIOWrapper, BytesIO
from septa.utils import find_model_by_plural_name, reset_primary_key_sequence
import requests

def import_septa_data(command: BaseCommand, zipfile: ZipFile, model_plural_name: str):
    batch_size = 10000
    model = find_model_by_plural_name(model_plural_name)
    objects_to_create: list[Model] = []
    created = 0
    with zipfile.open(f'{model_plural_name}.txt', 'r') as f:
        reader = DictReader(TextIOWrapper(f, 'utf-8'))
        reset_primary_key_sequence(model)
        for row in reader:
            model_data = {}
            for heading in reader.fieldnames:
                if row[heading] and hasattr(model, heading):
                    model_data.update({heading:row[heading]})
            objects_to_create.append(model(**model_data))
            if len(objects_to_create) == batch_size:
                model.objects.bulk_create(objects_to_create) 
                command.stdout.write(f"Created batch of {len(objects_to_create)} {model._meta.verbose_name_plural.capitalize()}, total: {created}")
                created += len(objects_to_create)
                objects_to_create.clear()
        if objects_to_create:
            model.objects.bulk_create(objects_to_create)
            created += len(objects_to_create)
            command.stdout.write(f"Created batch of {len(objects_to_create)} {model._meta.verbose_name_plural.capitalize()}, total: {created}")

def get_septa_bus_zipfile(command: BaseCommand, url: str):
    command.stdout.write(command.style.SUCCESS('Contacting Septa for Routes'))
    response = requests.get(url)
    response.raise_for_status()
    with ZipFile(BytesIO(response.content)) as zf_outer:
        bus_filename = 'google_bus.zip'
        if bus_filename not in zf_outer.namelist():
            command.stderr.write(f"GTFS File doesn't include {bus_filename}")
            return []
        else:
            bus_zip_file = ZipFile(BytesIO(zf_outer.read(bus_filename)))
            return bus_zip_file

