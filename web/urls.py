from django.urls import path
from web import views


urlpatterns = [
    path('', views.main_test),
    path('<slug:slug>/', views.details_test),
]
