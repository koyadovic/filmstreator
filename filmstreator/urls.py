from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from core.robots.proxys import process_new_proxy_files

urlpatterns = [
    path('ad/', admin.site.urls),
    path('', include('web.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


process_new_proxy_files()
