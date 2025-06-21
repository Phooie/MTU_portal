from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth import get_user_model
import json
from django.utils import timezone



from django.db import models
from django.contrib.auth.models import User

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     search_history = models.JSONField(default=list, help_text="Stores past search queries")
#     recommended_items = models.JSONField(default=list, help_text="Stores recommended resources")

#     def add_search_query(self, query):
#         """Append new search query only if it's not already stored."""
#         if query and query not in self.search_history:
#             self.search_history.append(query)
#             self.save(update_fields=['search_history'])


#     def update_recommendations(self, recommendations):
#         """Store recommended items only if they are unique."""
#         serialized_recommendations = [
#             {
#                 "title": item.title,
#                 "description": item.description,
#                 "category": item.category,
#                 "link": item.link if hasattr(item, "link") else None
#             }
#             for item in recommendations
#         ]

#         # Ensure only unique recommendations are stored
#         existing_titles = {rec["title"] for rec in self.recommended_items}
#         unique_recommendations = [rec for rec in serialized_recommendations if rec["title"] not in existing_titles]

#         if unique_recommendations:
#             self.recommended_items.extend(unique_recommendations)
#             self.save(update_fields=['recommended_items'])




class EngineeringBook(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    download_link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        blank=True,
        help_text="Official/publisher link for the book"
    )
    description = models.CharField(
        max_length=20,
        blank=True,
        help_text="Summary of the contents"
    )
    
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('CE', 'Civil Engineering'),
            ('ME', 'Mechanical Engineering'),
            ('EP', 'Electrical Power Engineering'),
            ('EC', 'Electronics Engineering'),
            ('CEIT', 'Computer Engineering and Information Technology'),
            ('MC', 'Mechatronics Engineering'),
            ('ChE', 'Chemical Engineering'),
            ('Agri', 'Agricultural Engineering'),
            ('MinE', 'Mining Engineering'),
            ('NE', 'Nuclear Engineering'),
            ('BioT', 'Biotechnology'),
            ('Arch', 'Architecture'),
            ('UNDEFINED', 'Undefined'),  # Explicitly added default choice
        ],
        default='UNDEFINED'  # Matches one of the choices above
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']  # Default sorting
        verbose_name = "Engineering Book"




from django.db import models

class Course_table(models.Model):
    title = models.CharField(max_length=200, null=False)
    instructor = models.CharField(max_length=200, null=False)
    description = models.TextField(blank=True)
    duration_weeks = models.IntegerField(default=4, help_text="Duration in weeks")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100)
    link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.title} - {self.instructor}"

    class Meta:
        ordering = ["start_date"]



from django.db import models

class Books_table(models.Model):
    title = models.CharField(max_length=200, null=False)
    author = models.CharField(max_length=200, null=False)
    description = models.TextField(blank=True)
    publication_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    category = models.CharField(max_length=100)
    link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ["publication_date"]



from django.db import models

class Research(models.Model):
    title = models.CharField(max_length=250, null=False)
    researcher = models.CharField(max_length=200, null=False)
    abstract = models.TextField(blank=True)
    publication_date = models.DateField(null=False)
    category = models.CharField(max_length=100)
    document_link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.title} by {self.researcher}"

    class Meta:
        ordering = ["-publication_date"]







class Course(models.Model):  # Singular name (convention for model classes)
    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=150)
    course_link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        blank=True,
        help_text="Link to the course"
    )

    category = models.CharField(
        max_length=50,
        choices=[
            ('CE', 'Civil Engineering'),
            ('ME', 'Mechanical Engineering'),
            ('EP', 'Electrical Power Engineering'),
            ('EC', 'Electronics Engineering'),
            ('CEIT', 'Computer Engineering and Information Technology'),
            ('MC', 'Mechatronics Engineering'),
            ('ChE', 'Chemical Engineering'),
            ('Agri', 'Agricultural Engineering'),
            ('MinE', 'Mining Engineering'),
            ('NE', 'Nuclear Engineering'),
            ('BioT', 'Biotechnology'),
            ('Arch', 'Architecture'),
            ('UNDEFINED', 'Undefined'),  # Explicitly added default choice
        ],
        default='UNDEFINED'  # Matches one of the choices above
    )

    def __str__(self):  # Fixed: Double underscores for magic method
        return f"{self.title} by {self.instructor}"

    class Meta:
        ordering = ['title']  # Default sorting
        verbose_name = "Engineering Course"  # Singular (optional)
        verbose_name_plural = "Engineering Courses"  # Plural name for admin panel




class Resource(models.Model):
    RESOURCE_TYPES = [
        ('BOOK', 'Book'),
        ('COURSE', 'Course'),
        ('EVENT', 'Event'),
        ('RESEARCH', 'Research'),
        ('NEWS', 'News'),
    ]

    instructor = models.CharField(max_length=150)
    link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        blank=True,
        help_text="Download link or link to the event"
    )

    category = models.CharField(
        max_length=50,
        choices=[
            ('CE', 'Civil Engineering'),
            ('ME', 'Mechanical Engineering'),
            ('EP', 'Electrical Power Engineering'),
            ('EC', 'Electronics Engineering'),
            ('CEIT', 'Computer Engineering and Information Technology'),
            ('MC', 'Mechatronics Engineering'),
            ('ChE', 'Chemical Engineering'),
            ('Agri', 'Agricultural Engineering'),
            ('MinE', 'Mining Engineering'),
            ('NE', 'Nuclear Engineering'),
            ('BioT', 'Biotechnology'),
            ('Arch', 'Architecture'),
            ('UNDEFINED', 'Undefined'),  # Explicitly added default choice
        ],
        default='UNDEFINED'  # Matches one of the choices above
    )
    
    # Common fields
    title = models.CharField(max_length=200)
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Summary of the contents"
    )
    resource_type = models.CharField(
        max_length=20, 
        choices=RESOURCE_TYPES)
    start_date = models.DateTimeField(blank=True, null=True)  # For events


    def __str__(self):  # Fixed: Double underscores for magic method
        return f"{self.title} by {self.instructor}"

    class Meta:
        ordering = ['title']  # Default sorting
        verbose_name = "Engineering links"  # Singular (optional)




# in models.py

from django.db import models
from django.core.validators import URLValidator

class News(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Short summary of the news")
    link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        blank=True,
        help_text="Optional link to full news"
    )

    start_date = models.DateTimeField(help_text="Date the news becomes visible")
    end_date = models.DateTimeField(
        blank=True, null=True, 
        help_text="Date after which the news is no longer active"
    )

    category = models.CharField(
        max_length=50,
        choices=[
            ('CE', 'Civil Engineering'),
            ('ME', 'Mechanical Engineering'),
            ('EP', 'Electrical Power Engineering'),
            ('EC', 'Electronics Engineering'),
            ('CEIT', 'Computer Engineering and Information Technology'),
            ('MC', 'Mechatronics Engineering'),
            ('ChE', 'Chemical Engineering'),
            ('Agri', 'Agricultural Engineering'),
            ('MinE', 'Mining Engineering'),
            ('NE', 'Nuclear Engineering'),
            ('BioT', 'Biotechnology'),
            ('Arch', 'Architecture'),
            ('UNDEFINED', 'Undefined'),
        ],
        default='UNDEFINED'
    )

    posted_by = models.CharField(max_length=150, help_text="Person or department posting the news")


    is_new = models.BooleanField(
        default=True,
        help_text="Set to True when the news is freshly added"
    )

    def __str__(self):
        return f"{self.title} ({self.category})"

    class Meta:
        ordering = ['-start_date']
        verbose_name = "News Item"
        verbose_name_plural = "News"



