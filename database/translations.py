from modeltranslation.translator import register, TranslationOptions
from .models import Student,Semester,Subject
from .books import Resource

@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('title', 'description','resource_type','category','instructor','description')  # Fields to translate

@register(Semester)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('semester', 'year')  # Fields to translate

@register(Student)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('student_name')  # Fields to translate


@register(Subject)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('name','semester')  # Fields to translate