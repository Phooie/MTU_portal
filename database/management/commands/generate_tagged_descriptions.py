import json

books = [...]  # Your JSON book data here

with open('tagged_description.txt', 'w') as f:
    for i, book in enumerate(books, 1):
        # Format title with underscores
        title = book['title'].replace(' ', '_')
        
        # Create tags
        tags = f"#{book['category']}"
        if 'majors' in book:
            tags += f" #{book['majors']}"
        
        # Special cases
        if "Study" in book['title']:
            tags += " #attendance"
        
        # Write line
        line = f"{i:03d} {title} {book['description']} {tags}\n"
        f.write(line)