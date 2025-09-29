from django.core.management.base import BaseCommand
from septa.management.commands._septa_client import get_septa_bus_zipfile, import_septa_data

class Command(BaseCommand):
    help = 'Attempt to download and parse routes from Septa'

    gtfs_url = "https://www3.septa.org/developer/gtfs_public.zip"
    
    DEFAULT_OPTIONS = {
        'verbosity',
        'settings',
        'pythonpath',
        'traceback',
        'no_color',
        'force_color',
        'skip_checks',
    }

    def add_arguments(self, parser):
        parser.add_argument('--routes', action='store_true')
        parser.add_argument('--stop_times', action='store_true')

        return super().add_arguments(parser)

    def handle(self, *args, **options):

        model_options = {
            key: value for key, value in options.items()
            if key not in self.DEFAULT_OPTIONS
        }

        if not any(model_options.values()):
            self.stderr.write(
                self.style.ERROR(
                    f"At least one option required: {' '.join(f"--{key}" for key in model_options.keys())}"
                )
            )
            return

        bus_zipfile = get_septa_bus_zipfile(self, self.gtfs_url)

        flagged_models = { 
            key: value for key, value in model_options.items()
            if value == True
        }
        for model in flagged_models.keys():
            import_septa_data(self, bus_zipfile, model)
        bus_zipfile.close()
        return