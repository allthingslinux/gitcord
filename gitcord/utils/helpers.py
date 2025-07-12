"""
Helper utilities for GitCord bot.
"""

from datetime import datetime
from typing import Optional, Union

import discord


def format_latency(latency: float) -> str:
    """
    Format latency in milliseconds.

    Args:
        latency: Latency in seconds

    Returns:
        Formatted latency string
    """
    return f"{round(latency * 1000)}ms"


def create_embed(
    title: str,
    description: str,
    color: Union[int, discord.Color] = discord.Color.blue(),
    author: Optional[discord.Member] = None,
    timestamp: Optional[datetime] = None,
    footer: Optional[str] = None
) -> discord.Embed:
    """
    Create a formatted Discord embed.

    Args:
        title: Embed title
        description: Embed description
        color: Embed color
        author: Optional author member
        timestamp: Optional timestamp
        footer: Optional footer text

    Returns:
        Formatted Discord embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=timestamp or datetime.utcnow()
    )

    if author:
        embed.set_author(
            name=author.display_name,
            icon_url=author.display_avatar.url
        )

    if footer:
        embed.set_footer(text=footer)

    return embed


def truncate_text(text: str, max_length: int = 1024) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."


def format_time_delta(seconds: float) -> str:
    """
    Format time delta in a human-readable format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    hours = seconds / 3600
    return f"{hours:.1f}h"
