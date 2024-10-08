# src/utils/logging_config.py


import logging
import warnings


def silence_all_warnings():
    # Ignore all warnings
    warnings.filterwarnings("ignore")


def get_logger(name):
    # Silence all warnings
    silence_all_warnings()

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False  # Prevent propagation to ancestor loggers

    return logger
