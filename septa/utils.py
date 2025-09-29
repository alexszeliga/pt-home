from django.apps import apps
from django.db import connection
from django.db.models import Model

def find_model_by_plural_name(plural_name:str):
    model_plural_name = plural_name.lower().replace("_"," ")
    for model in apps.get_models():
        if model._meta.verbose_name_plural.lower() == model_plural_name:
            return model
    return None

def reset_primary_key_sequence(model: Model):
    table_name = model._meta.db_table
    
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
