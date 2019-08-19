from sentry_sdk import capture_exception, capture_message
import traceback
import logging


# By now, we integrate Sentry here
file_logger = logging.getLogger('filmstreator')


def log_message(message: str, only_file=False):
    file_logger.info(message)
    if only_file:
        return
    capture_message(message)


def log_exception(exception: Exception, only_file=False):
    file_logger.exception(exception)
    file_logger.error(traceback.format_exc())
    if only_file:
        return
    capture_exception(exception)
