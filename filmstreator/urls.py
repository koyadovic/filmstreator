from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('ad/', admin.site.urls),
    path('', include('web.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = 'web.views.page404'
handler500 = 'web.views.page500'
