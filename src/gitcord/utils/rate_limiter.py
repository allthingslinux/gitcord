"""
Rate limiting utilities for GitCord bot commands.
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
from functools import wraps

import discord
from discord.ext import commands

from ..constants.messages import ERR_RATE_LIMITED
from .helpers import create_error_embed


# Hard-coded rate limiting configuration
RATE_LIMIT_MAX_COMMANDS = 1  # 1 command per window
RATE_LIMIT_WINDOW = 5       # 5 second window


class RateLimiter:
    """Rate limiter for bot commands."""
    
    def __init__(self):
        """Initialize the rate limiter."""
        # Dict[user_id, deque[timestamp]]
        self._user_timestamps: Dict[int, Deque[float]] = defaultdict(deque)
        # Dict[user_id, last_rate_limit_message_time]
        self._last_rate_limit_message: Dict[int, float] = {}
    
    def is_rate_limited(self, user_id: int) -> Tuple[bool, float]:
        """
        Check if a user is rate limited.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Tuple of (is_limited, time_until_reset)
        """
        current_time = time.time()
        user_timestamps = self._user_timestamps[user_id]
        
        # Remove old timestamps outside the window
        window_start = current_time - RATE_LIMIT_WINDOW
        while user_timestamps and user_timestamps[0] < window_start:
            user_timestamps.popleft()
        
        # Check if user has exceeded the limit
        if len(user_timestamps) >= RATE_LIMIT_MAX_COMMANDS:
            # Calculate time until reset
            oldest_timestamp = user_timestamps[0]
            time_until_reset = RATE_LIMIT_WINDOW - (current_time - oldest_timestamp)
            return True, max(0, time_until_reset)
        
        return False, 0.0
    
    def add_command_usage(self, user_id: int) -> None:
        """
        Record a command usage for a user.
        
        Args:
            user_id: Discord user ID
        """
        current_time = time.time()
        self._user_timestamps[user_id].append(current_time)
    
    def should_send_rate_limit_message(self, user_id: int) -> bool:
        """
        Check if we should send a rate limit message to avoid spam.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if we should send the message, False if we sent one recently
        """
        current_time = time.time()
        last_message_time = self._last_rate_limit_message.get(user_id, 0)
        
        # Only send rate limit message once every 30 seconds per user
        if current_time - last_message_time >= 30:
            self._last_rate_limit_message[user_id] = current_time
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit():
    """
    Decorator to add rate limiting to commands.
    
    Usage:
        @rate_limit()
        @commands.command()
        async def my_command(self, ctx):
            # Command logic here
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            user_id = ctx.author.id
            
            # Check if user is rate limited
            is_limited, time_until_reset = rate_limiter.is_rate_limited(user_id)
            
            if is_limited:
                # Only send rate limit message if we haven't sent one recently
                if rate_limiter.should_send_rate_limit_message(user_id):
                    embed = create_error_embed(
                        "⏰ Rate Limited",
                        ERR_RATE_LIMITED.format(
                            time_left=f"{time_until_reset:.1f}",
                            max_commands=RATE_LIMIT_MAX_COMMANDS,
                            window=RATE_LIMIT_WINDOW
                        )
                    )
                    await ctx.send(embed=embed, delete_after=10)
                return
            
            # Record command usage
            rate_limiter.add_command_usage(user_id)
            
            # Execute the original command
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit_app_command():
    """
    Decorator to add rate limiting to app commands (slash commands).
    
    Usage:
        @rate_limit_app_command()
        @app_commands.command()
        async def my_slash_command(self, interaction):
            # Command logic here
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            user_id = interaction.user.id
            
            # Check if user is rate limited
            is_limited, time_until_reset = rate_limiter.is_rate_limited(user_id)
            
            if is_limited:
                # Only send rate limit message if we haven't sent one recently
                if rate_limiter.should_send_rate_limit_message(user_id):
                    embed = create_error_embed(
                        "⏰ Rate Limited",
                        ERR_RATE_LIMITED.format(
                            time_left=f"{time_until_reset:.1f}",
                            max_commands=RATE_LIMIT_MAX_COMMANDS,
                            window=RATE_LIMIT_WINDOW
                        )
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    # If we've already sent a message recently, just fail silently
                    if not interaction.response.is_done():
                        await interaction.response.defer(ephemeral=True)
                return
            
            # Record command usage
            rate_limiter.add_command_usage(user_id)
            
            # Execute the original command
            return await func(self, interaction, *args, **kwargs)
        
        return wrapper
    return decorator