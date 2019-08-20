from sentry_sdk import capture_exception, capture_message
import logging

logger = logging.getLogger('core.tools.logs')


def log_message(message: str, only_file=False):
    logger.info(message)
    if only_file:
        return
    capture_message(message)


def log_exception(exception: Exception, only_file=False):
    logger.info(exception)
    if only_file:
        return
    capture_exception(exception)
