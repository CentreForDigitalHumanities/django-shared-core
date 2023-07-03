"""Helper functions to attach loggers to a Django shell.

It's not hard to do, but a pain to type in.
"""
import logging
import sys
from typing import Optional

_handlers = []


class CustomFormatter(logging.Formatter):
    """Custom formatter to log with colors"""

    gray = "\x1b[37;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] |%(name)s| %(levelname)-8s %(message)s - {%(filename)s:%(lineno)d}" # NoQA

    def __init__(self, format):
        super().__init__()
        if format:
            self.format = format

    FORMATS = {
        logging.DEBUG: gray + format + reset,
        logging.INFO: gray + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def attach_logger_to_shell(
        name: str,
        log_format: Optional[str] = None,
        level: str = 'DEBUG',
        stream=sys.stdout,
):
    """Attaches a given logger to the shell, by default using stdout and logger
    level DEBUG.

    :param name: The name of the logger to attach. None to get all (NOT
    RECOMMENDED)
    :param log_format: (Optional) a custom log format if the default is not
    nice enough
    :param level: (Optional) minimum logging level to log. Defaults to DEBUG
    :param stream: (Optional) the output to log to. Must be an IO stream.
    Defaults to stdout
    :return: The created handler (can be used to detach it specifically later)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = CustomFormatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _handlers.append(handler)

    return handler


def detach_logger(name: Optional[str] = None):
    """Detaches all handlers for a given logger. Will not remove handlers
    that weren't added by attach_logger_to_shell
    """
    for handler in _handlers:
        detach_handler(handler, name)


def detach_handler(handler, name: Optional[str] = None):
    """Detaches a given handler for a given logger. Will not remove handlers
    that weren't added by attach_logger_to_shell"""
    logger = logging.getLogger(name)
    if handler in logger.handlers and handler in _handlers:
        logging.getLogger(name).removeHandler(handler)

        _handlers.remove(handler)
