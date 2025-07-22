"""
Category management utilities for GitCord bot.
"""

from dataclasses import dataclass
from typing import List, Optional

import discord

from .helpers import create_embed, parse_channel_config
from .logger import main_logger as logger

import requests


@dataclass
class CategoryResult:
    """Result of category processing operations."""

    created_channels: List[discord.abc.GuildChannel]
    updated_channels: List[discord.abc.GuildChannel]
    skipped_channels: List[str]
    extra_channels: List[discord.abc.GuildChannel]
    category_updated: bool


async def process_existing_category(
    guild: discord.Guild,
    category_config: dict,
    existing_category: discord.CategoryChannel,
    category_position: int = None,
) -> CategoryResult:
    """
    Process an existing category and update/create channels as needed.

    Args:
        guild: The Discord guild
        category_config: The category configuration from YAML
        existing_category: The existing category channel
        category_position: The desired position of the category based on YAML order

    Returns:
        CategoryResult with processing results
    """
    yaml_channel_names = _get_yaml_channel_names(category_config)
    extra_channels = _find_extra_channels(
        existing_category, yaml_channel_names, category_config["name"]
    )

    # Update category position if needed (smart positioning)
    category_updated = False
    if category_position is not None:
        # Get all categories in guild sorted by position
        guild_categories = sorted(guild.categories, key=lambda cat: cat.position)
        current_relative_index = guild_categories.index(existing_category)
        
        # Only move if the category is not at the correct relative position
        if current_relative_index != category_position:
            try:
                await existing_category.edit(position=category_position)
                logger.info(
                    "Updated category '%s' position to %d",
                    category_config["name"],
                    category_position,
                )
                category_updated = True
            except (discord.Forbidden, discord.HTTPException) as e:
                logger.warning("Failed to update category position: %s", e)

    # Process channels in the category
    created_channels, updated_channels, skipped_channels = (
        await _process_category_channels(guild, existing_category, category_config)
    )

    return CategoryResult(
        created_channels=created_channels,
        updated_channels=updated_channels,
        skipped_channels=skipped_channels,
        extra_channels=extra_channels,
        category_updated=category_updated,
    )


def _get_yaml_channel_names(category_config: dict) -> set:
    """Get set of channel names from YAML configuration."""
    yaml_channel_names = set()
    for channel_name in category_config["channels"]:
        try:
            channel_yaml_path = f"{channel_name}.yaml"
            channel_config = parse_channel_config(channel_yaml_path)
            yaml_channel_names.add(channel_config["name"])
        except (ValueError, FileNotFoundError) as e:
            logger.error(
                "Failed to parse channel '%s' from YAML: %s",
                channel_name,
                e,
            )
    return yaml_channel_names


def _find_extra_channels(
    existing_category: discord.CategoryChannel,
    yaml_channel_names: set,
    category_name: str,
) -> List[discord.abc.GuildChannel]:
    """Find channels that exist in Discord but not in YAML."""
    extra_channels = []
    for existing_channel in existing_category.channels:
        if existing_channel.name not in yaml_channel_names:
            extra_channels.append(existing_channel)
            logger.info(
                "Found extra channel '%s' in category '%s' (not in YAML)",
                existing_channel.name,
                category_name,
            )
    return extra_channels


async def _process_category_channels(
    guild: discord.Guild,
    existing_category: discord.CategoryChannel,
    category_config: dict,
) -> tuple[
    List[discord.abc.GuildChannel], List[discord.abc.GuildChannel], List[str]
]:
    """Process channels in the category."""
    created_channels = []
    updated_channels = []
    skipped_channels = []

    channels = category_config.get("channels", [])
    for channel_index, channel_name in enumerate(channels):
        try:
            channel_yaml_path = f"{channel_name}.yaml"
            channel_config = parse_channel_config(channel_yaml_path)

            existing_channel = discord.utils.get(
                existing_category.channels, name=channel_config["name"]
            )

            if existing_channel:
                channel_updated = await _update_existing_channel(
                    existing_channel, channel_config, category_config["name"], channel_index
                )
                if channel_updated:
                    updated_channels.append(existing_channel)
                else:
                    skipped_channels.append(channel_config["name"])
            else:
                new_channel = await _create_channel_in_category(
                    guild, channel_config, existing_category, category_config["name"], channel_index
                )
                if new_channel:
                    created_channels.append(new_channel)

        except (ValueError, FileNotFoundError) as e:
            logger.error(
                "Failed to parse channel '%s' from YAML: %s",
                channel_name,
                e,
            )
            skipped_channels.append(channel_name)

    return created_channels, updated_channels, skipped_channels


async def _update_existing_channel(
    existing_channel: discord.abc.GuildChannel,
    channel_config: dict,
    category_name: str,
    channel_position: int = None,
) -> bool:
    """Update an existing channel with new configuration."""
    channel_updated = False
    update_kwargs = {}

    # Check if topic needs updating (text channels only)
    if (
        channel_config["type"].lower() == "text"
        and hasattr(existing_channel, "topic")
        and existing_channel.topic != channel_config.get("topic", "")
    ):
        update_kwargs["topic"] = channel_config.get("topic", "")
        channel_updated = True

    # Check if NSFW setting needs updating
    if (
        hasattr(existing_channel, "nsfw")
        and existing_channel.nsfw != channel_config.get("nsfw", False)
    ):
        update_kwargs["nsfw"] = channel_config.get("nsfw", False)
        channel_updated = True

    # Check if position needs updating based on YAML order (smart positioning)
    if (
        channel_position is not None
        and hasattr(existing_channel, "position")
    ):
        # Get all channels in category sorted by position  
        category_channels = sorted(existing_channel.category.channels, key=lambda ch: ch.position)
        current_relative_index = category_channels.index(existing_channel)
        
        # Only move if the channel is not at the correct relative position
        if current_relative_index != channel_position:
            update_kwargs["position"] = channel_position
            channel_updated = True

    if channel_updated:
        try:
            await existing_channel.edit(**update_kwargs)
            position_msg = f" (moved to position {channel_position})" if channel_position is not None and "position" in update_kwargs else ""
            logger.info(
                "Updated channel '%s' in category '%s'%s",
                channel_config["name"],
                category_name,
                position_msg,
            )
            return True
        except (discord.Forbidden, discord.HTTPException) as e:
            logger.error(
                "Failed to update channel '%s': %s",
                channel_config["name"],
                e,
            )

    return False


async def _create_channel_in_category(
    guild: discord.Guild,
    channel_config: dict,
    category: discord.CategoryChannel,
    category_name: str,
    channel_position: int = None,
) -> Optional[discord.abc.GuildChannel]:
    """Create a new channel in the specified category."""
    try:
        channel_kwargs = {
            "name": channel_config["name"],
            "category": category,
        }

        # Add topic if specified
        if "topic" in channel_config:
            channel_kwargs["topic"] = channel_config["topic"]

        # Add NSFW setting if specified
        if "nsfw" in channel_config:
            channel_kwargs["nsfw"] = channel_config["nsfw"]
        
        # Add position if specified (for YAML order-based positioning)
        if channel_position is not None:
            channel_kwargs["position"] = channel_position

        channel_type = channel_config["type"].lower()

        if channel_type == "text":
            new_channel = await guild.create_text_channel(**channel_kwargs)
        elif channel_type == "voice":
            # Voice channels don't support topic, so remove it if present
            if "topic" in channel_kwargs:
                del channel_kwargs["topic"]
            new_channel = await guild.create_voice_channel(**channel_kwargs)
        else:
            logger.error("Unknown channel type: %s", channel_type)
            return None

        position_msg = f" at position {channel_position}" if channel_position is not None else ""
        logger.info(
            "Created %s channel '%s' in category '%s'%s",
            channel_type,
            channel_config["name"],
            category_name,
            position_msg,
        )
        return new_channel

    except (discord.Forbidden, discord.HTTPException) as e:
        logger.error(
            "Failed to create channel '%s' in category '%s': %s",
            channel_config["name"],
            category_name,
            e,
        )
        return None


def create_category_result_embed(
    category_name: str,
    result: CategoryResult,
) -> discord.Embed:
    """Create an embed showing category processing results."""
    embed = create_embed(
        title="✅ Category Processed",
        description=f"Successfully processed category: **{category_name}**",
        color=discord.Color.green(),
    )

    # Add fields
    embed.add_field(name="Category", value=f"**{category_name}**", inline=True)
    if result.category_updated:
        embed.add_field(name="Category Updated", value="✅ Position", inline=True)
    else:
        embed.add_field(name="Category Updated", value="❌ No changes", inline=True)
    
    embed.add_field(
        name="Channels Created",
        value=str(len(result.created_channels)),
        inline=True,
    )
    embed.add_field(
        name="Channels Updated",
        value=str(len(result.updated_channels)),
        inline=True,
    )
    embed.add_field(
        name="Channels Skipped",
        value=str(len(result.skipped_channels)),
        inline=True,
    )
    embed.add_field(
        name="Extra Channels", value=str(len(result.extra_channels)), inline=True
    )

    if result.created_channels:
        channel_list = "\n".join(
            [f"• {channel.mention} (new)" for channel in result.created_channels]
        )
        embed.add_field(name="New Channels", value=channel_list, inline=False)

    if result.updated_channels:
        channel_list = "\n".join(
            [f"• {channel.mention} (updated)" for channel in result.updated_channels]
        )
        embed.add_field(name="Updated Channels", value=channel_list, inline=False)

    if result.extra_channels:
        channel_list = "\n".join(
            [f"• {channel.mention} (not in YAML)" for channel in result.extra_channels]
        )
        embed.add_field(
            name="Extra Channels (Not in YAML)",
            value=channel_list,
            inline=False,
        )

    return embed


async def handle_category_response(
    interaction: discord.Interaction,
    embed: discord.Embed,
    extra_channels: List[discord.abc.GuildChannel],
    category_name: str,
) -> None:
    """Handle the response for category processing."""
    if extra_channels:
        delete_view = DeleteExtraChannelsView(extra_channels, category_name)
        await interaction.followup.send(embed=embed, view=delete_view)
    else:
        await interaction.followup.send(embed=embed)
