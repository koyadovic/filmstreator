from filmstreator.settings.base import *

DEBUG = True

FILMSTREATOR_LOG_FILENAME = BASE_DIR + '/logs/filmstreator-debug.log'

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
        'core.tools.logs': {
            'handlers': ['filmstreator'],
            'level': 'DEBUG'
        },
    }
}
