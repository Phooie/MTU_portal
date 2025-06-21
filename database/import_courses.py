from django.core.management.base import BaseCommand
from database.books import Course
import json

class Command(BaseCommand):
    help = 'Import MTU courses from JSON'

    def handle(self, *args, **options):
        with open('database/mtu_all_courses.json', 'r') as file:  # Updated path
            data = json.load(file)
            created_count = 0
            for item in data:
                Course.objects.create(**item)
                created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {created_count} courses'
                )
            )