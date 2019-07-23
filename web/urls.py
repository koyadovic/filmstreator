from django.urls import path
from web import views


urlpatterns = [
    path('api/v1/genres/', views.search),
    path('api/v1/persons/', views.search),
    path('api/v1/filter/', views.search),
    path('', views.landing),
    path('<slug:slug>/', views.details),
]
