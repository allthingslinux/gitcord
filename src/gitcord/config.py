"""
Configuration module for GitCord bot.
Handles environment variables and bot settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for GitCord bot settings."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._token: Optional[str] = None
        self._prefix: str = "!"
        self._activity_name: str = "!hello"
        
        # Rate limiting configuration
        self._rate_limit_max_commands: int = int(os.getenv("RATE_LIMIT_MAX_COMMANDS", "1"))
        self._rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "5"))
        self._rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    @property
    def token(self) -> str:
        """Get Discord bot token from environment variables."""
        if not self._token:
            self._token = os.getenv("DISCORD_TOKEN")
            if not self._token:
                raise ValueError("DISCORD_TOKEN not found in environment variables!")
        return self._token

    @property
    def prefix(self) -> str:
        """Get command prefix."""
        return self._prefix

    @property
    def activity_name(self) -> str:
        """Get bot activity name."""
        return self._activity_name

    @activity_name.setter
    def activity_name(self, value: str) -> None:
        """Set bot activity name."""
        self._activity_name = value

    @property
    def rate_limit_max_commands(self) -> int:
        """Get maximum number of commands allowed per time window."""
        return self._rate_limit_max_commands

    @property
    def rate_limit_window(self) -> int:
        """Get rate limiting time window in seconds."""
        return self._rate_limit_window

    @property
    def rate_limit_enabled(self) -> bool:
        """Get whether rate limiting is enabled."""
        return self._rate_limit_enabled

    @rate_limit_enabled.setter
    def rate_limit_enabled(self, value: bool) -> None:
        """Set whether rate limiting is enabled."""
        self._rate_limit_enabled = value


# Global configuration instance
config = Config()
