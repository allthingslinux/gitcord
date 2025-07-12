"""
Logging utilities for GitCord bot.
"""

import logging
from typing import Optional


def setup_logger(name: str = "gitcord", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with proper formatting.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None) -> None:
    """
    Log an error with context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Optional context string
    """
    message = f"Error: {error}"
    if context:
        message = f"{context} - {message}"
    logger.error(message, exc_info=True)


# Default logger instance
logger = setup_logger()
