import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps

class Command(BaseCommand):
    help = 'Load SQLite data (exported as JSON) into MySQL database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')
        parser.add_argument('--truncate', action='store_true', help='Delete existing data before import')

    def handle(self, *args, **options):
        json_file = options['json_file']
        truncate = options['truncate']

        try:
            # Load JSON data
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON data should be an array of objects")

            # Organize data by model
            model_data = {}
            for item in data:
                model_name = item['model']
                if model_name not in model_data:
                    model_data[model_name] = []
                model_data[model_name].append(item)

            # Process each model
            with transaction.atomic():
                for model_name, items in model_data.items():
                    # Get the model class
                    try:
                        app_label, model_class_name = model_name.split('.')
                        model = apps.get_model(app_label, model_class_name)
                    except (ValueError, LookupError) as e:
                        self.stdout.write(self.style.WARNING(f"Skipping unknown model: {model_name}"))
                        continue

                    # Truncate if requested
                    if truncate:
                        model.objects.all().delete()
                        self.stdout.write(self.style.WARNING(f'Truncated {model_name} table'))

                    # Prepare and create objects
                    created_count = 0
                    for item in items:
                        fields = item['fields']
                        pk = item.get('pk')
                        
                        # Handle special cases like M2M fields
                        m2m_fields = {}
                        regular_fields = {}
                        for field_name, value in fields.items():
                            if '__' in field_name:  # Handle nested fields if any
                                continue
                            if hasattr(model, field_name) and hasattr(getattr(model, field_name), 'through'):
                                m2m_fields[field_name] = value
                            else:
                                regular_fields[field_name] = value
                        
                        # Create the object
                        if pk:
                            obj, created = model.objects.update_or_create(
                                pk=pk,
                                defaults=regular_fields
                            )
                        else:
                            obj = model.objects.create(**regular_fields)
                            created = True
                        
                        # Handle M2M relationships
                        for field_name, values in m2m_fields.items():
                            if values:  # Only process if there are values
                                m2m_field = getattr(obj, field_name)
                                m2m_field.set(values)
                        
                        if created:
                            created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully imported {created_count} records into {model_name}'
                        )
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {str(e)}'))
            raise