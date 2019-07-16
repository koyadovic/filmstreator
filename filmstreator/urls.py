from django.contrib import admin
from django.urls import path
from django.conf import settings

import sentry_sdk

from implementations.mongodb.dao import DAOMongoDB
from implementations.mongodb.searches import SearchMongoDB
from sentry_sdk.integrations.django import DjangoIntegration
from core import services


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


# TODO remove or True. Enabled by now for tests
if settings.DEBUG or True:
    sentry_sdk.init(
        dsn="https://3f87cf408a0042fc929df4e3ec80e390@sentry.io/1505406",
        integrations=[DjangoIntegration()]
    )
