from django.urls import path
from web import views


urlpatterns = [
    path('api/v1/genres/', views.genres),
    path('api/v1/people/', views.people),
    path('api/v1/search/', views.search),
    path('', views.landing),
    path('<slug:slug>/', views.details),
]
