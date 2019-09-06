from filmstreator.settings.base import *
from sentry_sdk.integrations.django import DjangoIntegration
import sentry_sdk


DEBUG = False

sentry_sdk.init(
    dsn="https://3f87cf408a0042fc929df4e3ec80e390@sentry.io/1505406",
    integrations=[DjangoIntegration()]
)

FILMSTREATOR_LOG_FILENAME = BASE_DIR + '/../../logs/filmstreator-debug.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s][%(asctime)s]:: %(message)s'
        }
    },
    'handlers': {
        'filmstreator': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': FILMSTREATOR_LOG_FILENAME,
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['filmstreator'],
            'level': 'WARNING'
        },
        'core.tools.logs': {
            'handlers': ['filmstreator'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
