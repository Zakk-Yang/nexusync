# logger.py 

import logging
from typing import Optional


def setup_logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """
    Set up and return a logger with the specified configuration.

    Args:
        name (str): The name of the logger. Defaults to the name of the current module.
        level (int): The logging level. Defaults to logging.INFO.
        log_file (Optional[str]): If provided, logs will be written to this file in addition to the console.
        format (str): The format string for the log messages.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # If a log file is specified, create a file handler
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
