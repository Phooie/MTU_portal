# scripts/load_books.py
import csv
from database.models import Book

def load_books_from_csv():
    with open('C:\Users\Dell\djangodb\database\engineering_books_by_category_and_major.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Example logic: categorize by genres or random
            Book.objects.create(
                title=row['title'],
                author=row['author'],
                download_link=row.get('download_link', ''),
                majors=row('majors'),
                description=row['description'] or "No description available."
            )
