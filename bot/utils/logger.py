import os
import logging
from logging.handlers import RotatingFileHandler
from config.config import config


def configure_logger(logger_name: str = None, log_file: str = None):
    """
    Configure a comprehensive logger with file and console output.

    Args:
        logger_name (str, optional): Name of the logger. Defaults to config.LOGGER_NAME.
        log_file (str, optional): Path to the log file. Defaults to config.LOGGER_FILE_NAME.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Use default values from config if not provided
    logger_name = logger_name or config.LOGGER_NAME
    log_file = log_file or config.LOGGER_FILE_NAME

    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Clear any existing handlers to prevent duplicate logging
    logger.handlers.clear()

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)

    # File Handler with log rotation
    file_handler = RotatingFileHandler(
        filename=log_file,
        mode="a",  # Append mode instead of overwrite
        maxBytes=10 * 1024 * 1024,  # 10 MB max file size
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create a global logger instance
logger = configure_logger()


def get_logger(name: str = None):
    """
    Get a child logger for a specific module.

    Args:
        name (str, optional): Module name. Defaults to None.

    Returns:
        logging.Logger: Child logger instance
    """
    return logger.getChild(name) if name else logger
