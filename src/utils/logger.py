"""Structured logging utility for ThinkTwice."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with a consistent format.

    Args:
        name: Logger name (typically ``__name__`` of the calling module).

    Returns:
        A :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
