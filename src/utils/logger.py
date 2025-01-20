import logging
import sys
from typing import Optional
from contextvars import ContextVar
from datetime import datetime

# Context variables to store user information
current_user_id: ContextVar[Optional[int]] = ContextVar('current_user_id', default=None)
current_username: ContextVar[Optional[str]] = ContextVar('current_username', default=None)


class TelegramUserFormatter(logging.Formatter):
    """Custom formatter that includes Telegram user information and timestamp in log messages"""
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m',  # Purple
        'RESET': '\033[0m'  # Reset color
    }

    def format(self, record):
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get user information from context
        try:
            user_id = current_user_id.get()
            username = current_username.get()
            user_info = f"[USER_ID:{user_id}|@{username}] " if user_id and username else ""
        except Exception:
            user_info = ""

        # Add color to the message
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.msg = f"{color}[{timestamp}] {user_info}{record.msg}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = "ZYA") -> logging.Logger:
    """
    Sets up and returns a logger for console output with Telegram user context

    Args:
        name: Logger name

    Returns:
        Configured Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Setup console handler with the custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(TelegramUserFormatter('%(message)s'))
    logger.addHandler(console_handler)

    return logger


# Create and export logger
logger = setup_logger()


def set_user_context(user_id: Optional[int], username: Optional[str]):
    """
    Sets the current user context for logging

    Args:
        user_id: Telegram user ID
        username: Telegram username
    """
    if user_id:
        current_user_id.set(user_id)
    if username:
        current_username.set(username)


def clear_user_context():
    """Clears the current user context"""
    current_user_id.set(None)
    current_username.set(None)