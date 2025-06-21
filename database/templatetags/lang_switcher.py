# your_app/templatetags/lang_switcher.py
from django import template
from django.urls import translate_url
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag(takes_context=True)
def change_lang(context, lang):
    request = context['request']
    current_lang = get_language()
    path = request.get_full_path()
    
    # Remove current language prefix if exists
    if path.startswith(f'/{current_lang}/'):
        path = path[len(current_lang)+2:]
    
    # Add new language prefix if not default
    if lang != 'en':  # Assuming 'en' is your default
        path = f'/{lang}{path}'
    
    return path