from django.db import models
from .books import Resource,Course_table
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

    

class Document(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    summary = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    student_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Changed from familyField
    date_joined = models.DateTimeField(auto_now_add=True)  # Fixed field name and type
    age = models.IntegerField()  # Fixed capitalization

    def __str__(self):
        return f"{self.student_id}"  # Fixed string formatting
    

class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('CLICK', 'Click'),
        ('SEARCH', 'Search')
    ]

    interaction_id = models.AutoField(primary_key=True)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column='student_id',
        related_name='interactions'
    )

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        db_column='resource_id',
        related_name='interactions',
        blank=True, null=True  # Allow null for search-only logs
    )

    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)

    weight = models.FloatField(default=1.0)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'database_interaction'  # Use this if you want to match table name explicitly
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.interaction_type} by {self.student} on {self.resource}"













class StudentAuth(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='auth')  # Fixed on_delete
    password_hash = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True)  # Fixed field type
    is_active = models.BooleanField(default=True)  # Fixed typo
    
    def __str__(self):
        return f"{self.student}"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)  # Fixed variable name

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)  # Fixed variable name

class Semester(models.Model):
    name = models.CharField(max_length=10)
    year = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} {self.year}"  # Fixed string formatting

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')  # Fixed on_delete

    def __str__(self):
        return f"{self.name} ({self.semester})"  # Fixed string formatting

# class StudentScore(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')  # Fixed on_delete
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')  # Fixed syntax
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='scores')
#     # Score breakdown
#     attendance = models.IntegerField(default=0)  # 0-10%
#     assignments = models.IntegerField(default=0)  # 0-20%
#     midterm = models.IntegerField(default=0)  # Fixed typo, 0-30%
#     final = models.IntegerField(default=0)  # 0-40%

#     class Meta:
#         unique_together = [['student', 'subject']]  # Prevent duplicate records

#     def clean(self):
#         if not (0 <= self.attendance <= 10):
#             raise ValidationError({'attendance': 'Must be between 0-10%'})
#         if not (0 <= self.assignments <= 20):
#             raise ValidationError({'assignments': 'Must be between 0-20%'})
#         if not (0 <= self.midterm <= 30):
#             raise ValidationError({'midterm': 'Must be between 0-30%'})
#         if not (0 <= self.final <= 40):
#             raise ValidationError({'final': 'Must be between 0-40%'})

#     @property
#     def total_score(self):
#         return self.attendance + self.assignments + self.midterm + self.final

#     def __str__(self):
#         return f"{self.student} - {self.subject}: {self.total_score}%"


class StudentScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='scores')
    # Updated score breakdown
    attendance = models.IntegerField(default=0)  # 0-100% (now excluded from total)
    assignments = models.IntegerField(default=0)  # 0-10%
    tutorial = models.IntegerField(default=0)     # 0-20%
    final = models.IntegerField(default=0)       # 0-40%

    class Meta:
        unique_together = [['student', 'subject']]

    def clean(self):
        if not (0 <= self.attendance <= 100):
            raise ValidationError({'attendance': 'Must be between 0-100%'})
        if not (0 <= self.assignments <= 10):
            raise ValidationError({'assignments': 'Must be between 0-10%'})
        if not (0 <= self.tutorial <= 10):
            raise ValidationError({'tutorial': 'Must be between 0-20%'})
        if not (0 <= self.final <= 80):
            raise ValidationError({'final': 'Must be between 0-40%'})

    @property
    def total_score(self):
        """Calculates total score from assignments (10%), tutorial (20%), and final (40%) only"""
        return self.assignments + self.tutorial + self.final  # Attendance excluded

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.total_score}%"
    




    from django.db import models
import json

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    # Store list of keywords or embeddings as JSON string
    keywords = models.TextField(blank=True)

    def set_keywords(self, keywords_list):
        self.keywords = json.dumps(keywords_list)

    def get_keywords(self):
        try:
            return json.loads(self.keywords)
        except Exception:
            return []
        

# class UserEnrollment(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE)  # Direct reference instead of separate UserProfile
#     course = models.ForeignKey(Course_table, on_delete=models.CASCADE)
#     enrollment_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.student.student_name} enrolled in {self.course.title}"


class UserEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Changed to ForeignKey
    course = models.ForeignKey(Course_table, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Optional: Add constraints if needed
        constraints = [
            # Example: Prevent duplicate active enrollments
            # models.UniqueConstraint(
            #     fields=['student', 'course'], 
            #     name='unique_enrollment',
            #     condition=models.Q(...)  # Add conditions if needed
            # )
        ]

    def __str__(self):
        return f"{self.student.student_name} enrolled in {self.course.title} (Enrollment ID: {self.id})"
    

class UserProfile(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    search_history = models.JSONField(default=list, help_text="Stores past search queries")
    recommended_items = models.JSONField(default=list, help_text="Stores recommended resources")
    created_at = models.DateTimeField(auto_now_add=True)

    def add_search_query(self, query):
        """Append new search query only if it's not already stored."""
        if query and query not in self.search_history:
            self.search_history.append(query)
            self.save(update_fields=['search_history'])

    def update_recommendations(self, recommendations):
        """Store recommended items only if they are unique."""
        serialized_recommendations = [
            {
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "link": item.link if hasattr(item, "link") else None
            }
            for item in recommendations
        ]

        existing_titles = {rec["title"] for rec in self.recommended_items}
        unique_recommendations = [rec for rec in serialized_recommendations if rec["title"] not in existing_titles]

        if unique_recommendations:
            self.recommended_items.extend(unique_recommendations)
            self.save(update_fields=['recommended_items'])

    def __str__(self):
        return f"Profile for {self.student.student_id}"

    class Meta:
        unique_together = ['student']  # Ensures one profile per student
