from django.contrib import admin
from django.urls import path

from implementations.mongodb_dao.dao import DAOMongoDB
from core import services


urlpatterns = [
    path('admin/', admin.site.urls),
]


def wire_implementations():
    print('lalala')
    dao = DAOMongoDB()
    services.inject_dao_interface_implementation(dao)


wire_implementations()
