from django.urls import path
from web import views


urlpatterns = [
    path('api/v1/genres/', views.genres),
    path('api/v1/people/', views.people),
    path('api/v1/audiovisual/', views.audiovisual),
    path('api/v1/landing/', views.landing_genres),
    path('', views.landing),
    path('<slug:slug>/', views.details),
]
