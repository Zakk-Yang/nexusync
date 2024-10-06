# utils/logging_config.py
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set the desired log level

    if not logger.handlers:
        # Configure handlers only if none exist
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = (
        False  # Prevent log messages from being propagated to ancestor loggers
    )

    return logger
