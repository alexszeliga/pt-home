from django.db import connection
from django.db.models import Model

def reset_primary_key_sequence(model: Model):
    table_name = model._meta.db_table
    
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")