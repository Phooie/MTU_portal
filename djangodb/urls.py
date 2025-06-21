from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# urlpatterns = [
#     path("admin/", admin.site.urls),

# ]

from django.conf import settings
from django.conf.urls.static import static  # Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('database.urls')),  # Your existing URL patterns
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('', include('database.urls')),  # All URLs that need translation
    prefix_default_language=False  # Important! Doesn't prefix default language
)