"""
Helper utilities for GitCord bot.
"""

import os
import re
from datetime import datetime
from typing import Optional, Union, List

import discord
import yaml
from discord.ext import commands


def format_latency(latency: float) -> str:
    """
    Format latency in milliseconds.

    Args:
        latency: Latency in seconds

    Returns:
        Formatted latency string
    """
    return f"{round(latency * 1000)}ms"


# pylint: disable=too-many-arguments, too-many-positional-arguments
def create_embed(
    title: str,
    description: str,
    color: Union[int, discord.Color] = discord.Color.from_str("#6f7dff"),
    author: Optional[discord.Member] = None,
    timestamp: Optional[datetime] = None,
    footer: Optional[str] = None,
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
        timestamp=timestamp or datetime.utcnow(),
    )

    if author:
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)

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

    return text[: max_length - 3] + "..."


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


def parse_channel_config(yaml_path: str) -> dict:
    """Parse and validate the YAML configuration file."""
    if not os.path.exists(yaml_path):
        raise ValueError(f"YAML file not found at: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as file:
        channel_config = yaml.safe_load(file)

    # Validate required fields
    required_fields = ["name", "type"]
    for field in required_fields:
        if field not in channel_config:
            raise ValueError(f"Missing required field: {field}")

    return channel_config


def parse_category_config(yaml_path: str) -> dict:
    """Parse and validate category YAML configuration file."""
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML file not found at: {yaml_path}")

    try:
        with open(yaml_path, "r", encoding="utf-8") as file:
            category_config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}") from e

    # Validate required fields
    required_fields = ["name", "type", "channels"]
    for field in required_fields:
        if field not in category_config:
            raise ValueError(f"Missing required field: {field}")

    return category_config


def parse_category_config_from_str(yaml_str: str) -> dict:
    """Parse and validate category YAML configuration from a string."""
    import yaml

    try:
        category_config = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}") from e
    if category_config is None:
        raise ValueError("YAML is empty or invalid.")
    required_fields = ["name", "type", "channels"]
    for field in required_fields:
        if field not in category_config:
            raise ValueError(f"Missing required field: {field}")
    return category_config


def parse_channel_config_from_str(yaml_str: str) -> dict:
    """Parse and validate channel YAML configuration from a string."""
    import yaml

    channel_config = yaml.safe_load(yaml_str)
    if channel_config is None:
        raise ValueError("YAML is empty or invalid.")
    required_fields = ["name", "type"]
    for field in required_fields:
        if field not in channel_config:
            raise ValueError(f"Missing required field: {field}")
    return channel_config


def create_channel_kwargs(
    channel_config: dict, category: Optional[discord.CategoryChannel] = None
) -> dict:
    """Create channel creation parameters from config."""
    channel_kwargs = {
        "name": channel_config["name"],
        "category": category,
    }

    # Add optional parameters if they exist
    if "topic" in channel_config:
        channel_kwargs["topic"] = channel_config["topic"]
    if "position" in channel_config:
        channel_kwargs["position"] = channel_config["position"]
    if "nsfw" in channel_config:
        channel_kwargs["nsfw"] = channel_config["nsfw"]

    return channel_kwargs


async def create_channel_by_type(
    guild: Optional[discord.Guild], channel_config: dict, channel_kwargs: dict
) -> Optional[discord.abc.GuildChannel]:
    """Create a channel based on its type."""
    if not guild:
        return None

    channel_type = channel_config["type"].lower()

    if channel_type == "text":
        return await guild.create_text_channel(**channel_kwargs)
    if channel_type == "voice":
        return await guild.create_voice_channel(**channel_kwargs)
    return None


def check_channel_exists(
    category: discord.CategoryChannel, channel_name: str
) -> Optional[discord.abc.GuildChannel]:
    """Check if a channel already exists in a category."""
    return discord.utils.get(category.channels, name=channel_name)


def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized error embed."""
    return create_embed(title=title, description=description, color=discord.Color.red())


def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized success embed."""
    return create_embed(
        title=title, description=description, color=discord.Color.green()
    )


def create_channel_list_embed(
    title: str,
    created_channels: List[discord.abc.GuildChannel],
    total_channels: int,
    category_name: str,
) -> discord.Embed:
    """Create an embed showing channel creation results."""
    embed = create_success_embed(
        title=title, description=f"Successfully processed category **{category_name}**"
    )

    embed.add_field(
        name="Channels Created",
        value=f"{len(created_channels)}/{total_channels}",
        inline=False,
    )

    if created_channels:
        channel_list = "\n".join(
            [f"• {channel.mention}" for channel in created_channels]
        )
        embed.add_field(name="Created Channels", value=channel_list, inline=False)

    return embed


async def handle_command_error(
    ctx: commands.Context, error: commands.CommandError, logger
) -> None:
    """Handle common command errors."""
    if isinstance(error, commands.MissingPermissions):
        embed = create_error_embed(
            "❌ Permission Denied", "You don't have permission to use this command."
        )
        await ctx.send(embed=embed)
        logger.error("Permission error in command")
    elif isinstance(error, discord.Forbidden):
        embed = create_error_embed(
            "❌ Permission Error",
            "The bot doesn't have permission to perform this action.",
        )
        await ctx.send(embed=embed)
        logger.error("Discord permission error in command")
    elif isinstance(error, discord.HTTPException):
        embed = create_error_embed(
            "❌ Discord Error", f"A Discord error occurred: {error}"
        )
        await ctx.send(embed=embed)
        logger.error(f"Discord HTTP error in command: {error}")
    else:
        embed = create_error_embed(
            "❌ Unexpected Error", f"An unexpected error occurred: {error}"
        )
        await ctx.send(embed=embed)
        logger.error(f"Unexpected error in command: {error}")


async def handle_interaction_error(
    interaction: discord.Interaction, error: Exception, logger
) -> None:
    """Handle common interaction errors."""
    if isinstance(error, discord.Forbidden):
        embed = create_error_embed(
            "❌ Permission Error",
            "The bot doesn't have permission to perform this action.",
        )
        await interaction.followup.send(embed=embed)
        logger.error("Discord permission error in interaction")
    elif isinstance(error, discord.HTTPException):
        embed = create_error_embed(
            "❌ Discord Error", f"A Discord error occurred: {error}"
        )
        await interaction.followup.send(embed=embed)
        logger.error(f"Discord HTTP error in interaction: {error}")
    else:
        embed = create_error_embed(
            "❌ Unexpected Error", f"An unexpected error occurred: {str(error)}"
        )
        await interaction.followup.send(embed=embed)
        logger.error(f"Unexpected error in interaction: {error}")


def clean_webpage_text(text: str, max_length: int = 1900) -> str:
    """Clean and truncate webpage text content."""
    # Clean up the text
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = " ".join(chunk for chunk in chunks if chunk)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Limit text length
    if len(text) > max_length:
        text = text[:max_length] + "...\n\n*Content truncated due to length limits*"

    return text
