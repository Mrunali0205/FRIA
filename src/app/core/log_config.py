"""
Setting up logging configuration for the application.
"""
import logging
import sys

def setup_logging(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        name (str): Name of the logger. Defaults to None.
        level (int): Logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logging.basicConfig(
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
