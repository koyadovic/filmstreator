from django.urls import path, re_path
from web import views
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/web/img/favicon.png', permanent=True)


urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),

    path('dmca/', views.dmca),
    path('404/', views.page404),
    path('500/', views.page500),

    # regular pages
    path('genres/<str:genre>/', views.genre_view),
    path('<slug:slug>/', views.details),
    path('', views.landing),
]
