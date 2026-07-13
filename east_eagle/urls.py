"""Root URL configuration for East Eagle Trading PLC."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
]

# Serve uploaded media (team photos) — needed on cPanel when Apache alias is not set
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
