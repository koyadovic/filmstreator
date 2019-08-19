from filmstreator.settings.base import *
from sentry_sdk.integrations.django import DjangoIntegration
import sentry_sdk


DEBUG = False


sentry_sdk.init(
    dsn="https://3f87cf408a0042fc929df4e3ec80e390@sentry.io/1505406",
    integrations=[DjangoIntegration()]
)

