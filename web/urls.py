from django.urls import path
from web import views


urlpatterns = [
    # for the dashboard/landing page, a simple API
    # path('api/v1/genres/', views.genres),
    # path('api/v1/people/', views.people),
    # path('api/v1/audiovisual/', views.audiovisual),
    # path('api/v1/landing/', views.landing_genres),

    path('dmca/', views.dmca),
    path('404/', views.page404),
    path('500/', views.page500),

    # regular pages
    path('genres/<str:genre>/', views.genre_view),
    path('<slug:slug>/', views.details),
    path('', views.landing),
]
