from django.urls import path, re_path
from web import views
from django.views.generic.base import RedirectView, TemplateView

favicon_view = RedirectView.as_view(url='/static/web/img/favicon.png', permanent=True)


urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name="web/robots.txt", content_type='text/plain')),
    re_path(r'^humans\.txt$', TemplateView.as_view(template_name="web/humans.txt", content_type='text/plain')),

    path('info/dmca/', views.dmca),
    path('info/terms-and-conditions/', views.terms_and_conditions),

    path('remove-download/<str:object_id>/', views.remove_download),
    path('remove-film/<str:object_id>/', views.remove_film),

    # regular pages
    path('best/<str:decade>/', views.best_decade),
    path('genres/<str:genre>/', views.genre_view),
    path('s/', views.landing),
    path('<slug:slug>/', views.details),
    path('', views.landing),
]
