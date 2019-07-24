from django.urls import path
from web import views


urlpatterns = [
    # for the dashboard/landing page, a simple API
    path('api/v1/genres/', views.genres),
    path('api/v1/people/', views.people),
    path('api/v1/audiovisual/', views.audiovisual),
    path('api/v1/landing/', views.landing_genres),

    # regular pages
    path('<slug:slug>/', views.details),
    path('', views.landing),
]
