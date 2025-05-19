"""Logger setup."""

import logging
from logging.handlers import RotatingFileHandler


LOG_DIR = "logs"

def setup_logging(logger_name: str="default") -> logging.Logger:
    """Sets up the logger and file handlers for DEBUG and ERROR as well as a stdout handler."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Handler for /log/app.log for all levels (DEBUG)
    app_log_handler = RotatingFileHandler(
        f"{LOG_DIR}/app.log",
        maxBytes=5*1024*1024, # 5 Mb
        backupCount=3
    )
    app_log_handler.setLevel(logging.DEBUG)
    app_log_handler.setFormatter(formatter)

    # Handler for /log/error.log for ERROR+CRITICAL levels
    error_log_handler = RotatingFileHandler(
        f"{LOG_DIR}/error.log",
        maxBytes=5*1024*1024,
        backupCount=3
    )
    error_log_handler.setLevel(logging.ERROR)
    error_log_handler.setFormatter(formatter)

    # stdout handler, all levels (DEBUG)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(app_log_handler)
    logger.addHandler(error_log_handler)
    logger.addHandler(stdout_handler)

    return logger
