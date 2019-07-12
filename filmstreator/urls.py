from django.contrib import admin
from django.urls import path

from core import services

from implementations.mongodb.dao import DAOMongoDB
from implementations.mongodb.searches import SearchMongoDB


urlpatterns = [
    path('admin/', admin.site.urls),
]


def wire_implementations():
    print('Wire implementations')
    dao_implementation = DAOMongoDB()
    search_implementation = SearchMongoDB()
    services.inject_dao_interface_implementation(dao_implementation)
    services.inject_search_interface_implementation(search_implementation)


wire_implementations()
