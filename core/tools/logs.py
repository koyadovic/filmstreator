import traceback

from sentry_sdk import capture_exception, capture_message

# By now, we integrate Sentry here


def log_message(message: str):
    capture_message(message)


def log_exception(exception: Exception):
    capture_exception(exception)
