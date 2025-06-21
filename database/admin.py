from django.contrib import admin
from .models import Student, StudentAuth, Semester, Subject, StudentScore, Document,UserEnrollment,UserProfile
from django import forms
from .books import EngineeringBook,Course,Resource,News,Books_table,Course_table,Research
from django.db.models import JSONField  # Updated import
from django.utils.html import format_html


# @admin.register(ResearchView)
# class ResearchViewAdmin(admin.ModelAdmin):
#     list_display = ('research', 'user', 'view_count', 'last_viewed')
#     list_filter = ('last_viewed',)
#     raw_id_fields = ('research', 'user')



@admin.register(Resource)
class Resource(admin.ModelAdmin):
    list_display = ('title', 'instructor','link','category','resource_type')
    search_fields = ('title', 'instructor', 'description')
    list_filter = ('category',)
    list_editable = ('category',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student_name', 'department')

# Register other models similarly
admin.site.register(StudentAuth)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(StudentScore)
admin.site.register(Course)
admin.site.register(EngineeringBook)
admin.site.register(Document)
admin.site.register(News)

# admin.site.register(Interaction)
admin.site.register(Books_table)

admin.site.register(Course_table)
admin.site.register(Research)
admin.site.register(UserEnrollment)
admin.site.register(UserProfile)




