"""
Channel management commands cog for GitCord bot.
Contains commands for creating and managing channels and categories.
"""

from dataclasses import dataclass
from typing import Optional, Union

import yaml
import discord
from discord import app_commands
from discord.ext import commands

from .base_cog import BaseCog
from ..utils.helpers import (
    create_embed,
    parse_channel_config,
    parse_category_config,
    create_channel_kwargs,
    create_channel_by_type,
    check_channel_exists,
)
from ..views import DeleteExtraChannelsView


@dataclass
class CategoryResult:
    """Result of category processing operations."""
    category: Optional[discord.CategoryChannel]
    created_channels: list
    updated_channels: list
    skipped_channels: list
    extra_channels: list
    is_update: bool


class Channels(BaseCog):
    """Channel management utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Channels cog."""
        super().__init__(bot)
        self.logger.info("Channels cog loaded")

    def _ensure_guild(
        self, ctx_or_interaction: Union[commands.Context, discord.Interaction]
    ) -> Optional[discord.Guild]:
        """Ensure we have a valid guild context."""
        if isinstance(ctx_or_interaction, commands.Context):
            return ctx_or_interaction.guild
        return ctx_or_interaction.guild

    def _ensure_permissions(
        self, ctx_or_interaction: Union[commands.Context, discord.Interaction]
    ) -> bool:
        """Check if user has manage channels permission."""
        if isinstance(ctx_or_interaction, commands.Context):
            # Type check to ensure author is a Member (has guild_permissions)
            if not isinstance(ctx_or_interaction.author, discord.Member):
                return False
            return ctx_or_interaction.author.guild_permissions.manage_channels
        # For interactions, we need to check if user is a member
        if ctx_or_interaction.user is None:
            return False
        # Type check to ensure user is a Member (has guild_permissions)
        if not isinstance(ctx_or_interaction.user, discord.Member):
            return False
        # At this point we know user is a Member, so we can safely access guild_permissions
        member = ctx_or_interaction.user  # type: discord.Member
        return member.guild_permissions.manage_channels

    async def _create_single_channel(
        self, ctx: commands.Context, yaml_path: str
    ) -> None:
        """Create a single channel from YAML configuration."""
        try:
            channel_config = parse_channel_config(yaml_path)
        except ValueError as e:
            await self.send_error(ctx, "❌ Invalid YAML", str(e))
            return

        # Prepare channel creation parameters
        channel_kwargs = create_channel_kwargs(channel_config)

        # Create the channel based on type
        new_channel = await create_channel_by_type(
            ctx.guild, channel_config, channel_kwargs
        )

        if not new_channel:
            await self.send_error(
                ctx,
                "❌ Invalid Channel Type",
                f"Channel type '{channel_config['type']}' is not supported. "
                "Use 'text' or 'voice'.",
            )
            return

        # Create success embed
        embed = create_embed(
            title="✅ Channel Created",
            description=f"Successfully created channel: {new_channel.mention}",
            color=discord.Color.green(),
        )

        # Add fields manually
        embed.add_field(name="Name", value=channel_kwargs["name"], inline=True)
        embed.add_field(name="Type", value=channel_config["type"], inline=True)
        embed.add_field(
            name="NSFW", value=channel_kwargs.get("nsfw", False), inline=True
        )
        embed.add_field(
            name="Topic",
            value=channel_config.get("topic", "No topic set"),
            inline=False,
        )

        await ctx.send(embed=embed)
        self.logger.info(
            "Channel '%s' created successfully by %s",
            channel_config["name"],
            ctx.author,
        )

    async def _update_existing_channel(
        self, existing_channel: discord.abc.GuildChannel, channel_config: dict
    ) -> bool:
        """Update an existing channel if needed."""
        channel_updated = False
        update_kwargs = {}

        # Check if it's a text channel for topic
        if isinstance(existing_channel, discord.TextChannel):
            if existing_channel.topic != channel_config.get("topic", ""):
                update_kwargs["topic"] = channel_config.get("topic", "")
                channel_updated = True

        # Check NSFW for text and voice channels
        if isinstance(existing_channel, (discord.TextChannel, discord.VoiceChannel)):
            if existing_channel.nsfw != channel_config.get("nsfw", False):
                update_kwargs["nsfw"] = channel_config.get("nsfw", False)
                channel_updated = True

        # Check position for all channel types
        if "position" in channel_config and hasattr(existing_channel, "position"):
            if existing_channel.position != channel_config["position"]:
                update_kwargs["position"] = channel_config["position"]
                channel_updated = True

        if not channel_updated:
            return False

        # Type check to ensure we can edit the channel
        if isinstance(existing_channel, (discord.TextChannel, discord.VoiceChannel)):
            await existing_channel.edit(**update_kwargs)
            self.logger.info(
                "Channel '%s' updated in category",
                channel_config["name"],
            )
            return True
        self.logger.warning(
            "Cannot edit channel '%s' of type %s",
            channel_config["name"],
            type(existing_channel).__name__,
        )
        return False

    async def _create_channel_in_category(
        self, guild: discord.Guild, channel_config: dict, category: discord.CategoryChannel
    ) -> Optional[discord.abc.GuildChannel]:
        """Create a new channel in the category."""
        channel_kwargs = create_channel_kwargs(channel_config, category)
        new_channel = await create_channel_by_type(guild, channel_config, channel_kwargs)

        if new_channel:
            self.logger.info(
                "Channel '%s' created successfully in category",
                channel_config["name"],
            )
            return new_channel
        self.logger.warning(
            "Skipping channel '%s': Invalid type '%s'",
            channel_config["name"],
            channel_config["type"],
        )
        return None

    async def _process_channel_in_category(
        self, guild: discord.Guild, existing_category: discord.CategoryChannel,
        channel_name: str, yaml_channel_names: set
    ) -> tuple[Optional[discord.abc.GuildChannel], Optional[discord.abc.GuildChannel], str]:
        """Process a single channel in a category."""
        try:
            channel_yaml_path = (
                f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
            )
            channel_config = parse_channel_config(channel_yaml_path)

            existing_channel = check_channel_exists(
                existing_category, channel_config["name"]
            )

            if existing_channel:
                if await self._update_existing_channel(existing_channel, channel_config):
                    yaml_channel_names.add(channel_config["name"])
                    return existing_channel, None, ""
                return None, None, channel_config["name"]

            new_channel = await self._create_channel_in_category(
                guild, channel_config, existing_category
            )
            if new_channel:
                yaml_channel_names.add(channel_config["name"])
                return None, new_channel, ""
            return None, None, ""

        except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
            self.logger.error(
                "Failed to create channel '%s': %s", channel_name, e
            )
            return None, None, ""

    async def _process_existing_category_channels(
        self,
        guild: discord.Guild,
        existing_category: discord.CategoryChannel,
        category_config: dict
    ) -> tuple[list, list, list, list]:
        """Process channels in an existing category."""
        updated_channels = []
        created_channels = []
        skipped_channels = []
        extra_channels = []
        yaml_channel_names = set()

        for channel_name in category_config["channels"]:
            updated_channel, new_channel, skipped_name = await self._process_channel_in_category(
                guild, existing_category, channel_name, yaml_channel_names
            )

            if updated_channel:
                updated_channels.append(updated_channel)
            elif new_channel:
                created_channels.append(new_channel)
            elif skipped_name:
                skipped_channels.append(skipped_name)

        # Find extra channels
        for channel in existing_category.channels:
            if channel.name not in yaml_channel_names:
                extra_channels.append(channel)

        return created_channels, updated_channels, skipped_channels, extra_channels

    async def _handle_existing_category(
        self,
        guild: discord.Guild,
        existing_category: discord.CategoryChannel,
        category_config: dict
    ) -> tuple[list, list, list, list]:
        """Handle processing of an existing category."""
        return await self._process_existing_category_channels(
            guild, existing_category, category_config
        )

    async def _create_new_category(
        self, guild: discord.Guild, category_config: dict
    ) -> tuple[discord.CategoryChannel, list]:
        """Create a new category with channels."""
        category_kwargs = {
            "name": category_config["name"],
            "position": category_config.get("position", 0),
        }
        new_category = await guild.create_category(**category_kwargs)
        created_channels = []

        for channel_name in category_config["channels"]:
            try:
                channel_yaml_path = (
                    f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                )
                channel_config = parse_channel_config(channel_yaml_path)

                existing_channel = check_channel_exists(
                    new_category, channel_config["name"]
                )
                if existing_channel:
                    self.logger.warning(
                        "Channel '%s' already exists in category '%s', skipping",
                        channel_config["name"],
                        category_config["name"],
                    )
                    continue

                new_channel = await self._create_channel_in_category(
                    guild, channel_config, new_category
                )
                if new_channel:
                    created_channels.append(new_channel)

            except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                self.logger.error("Failed to create channel '%s': %s", channel_name, e)
                continue

        return new_category, created_channels

    async def _create_category_common(
        self,
        guild: discord.Guild,
        yaml_path: str
    ) -> CategoryResult:
        """Common logic for creating/updating categories."""
        try:
            category_config = parse_category_config(yaml_path)
        except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
            self.logger.error("Failed to parse category config: %s", e)
            return CategoryResult(None, [], [], [], [], False)

        # Check if category already exists
        existing_category = discord.utils.get(
            guild.categories, name=category_config["name"]
        )

        if existing_category:
            # Category exists, process it
            created_channels, updated_channels, skipped_channels, extra_channels = (
                await self._handle_existing_category(guild, existing_category, category_config)
            )
            return CategoryResult(
                existing_category, created_channels, updated_channels,
                skipped_channels, extra_channels, True
            )
        # Create new category
        new_category, created_channels = await self._create_new_category(
            guild, category_config
        )
        return CategoryResult(new_category, created_channels, [], [], [], False)

    def _add_channel_list_field(
        self, embed: discord.Embed, channels: list, field_name: str
    ) -> None:
        """Add a channel list field to an embed."""
        if channels:
            channel_list = "\n".join(
                [f"• {channel.mention} ({field_name.lower()})" for channel in channels]
            )
            embed.add_field(
                name=f"{field_name} Channels", value=channel_list, inline=False
            )

    def _create_category_result_embed(self, result: CategoryResult) -> discord.Embed:
        """Create result embed for category operations."""
        if not result.category:
            raise ValueError("Category cannot be None when creating result embed")

        title = "✅ Category Updated" if result.is_update else "✅ Category Created"
        description = f"Successfully processed category: **{result.category.name}**"

        embed = create_embed(
            title=title,
            description=description,
            color=discord.Color.green(),
        )

        # Add basic fields
        embed.add_field(name="Category", value=result.category.mention, inline=True)
        embed.add_field(
            name="Channels Created", value=str(len(result.created_channels)), inline=True
        )
        embed.add_field(
            name="Channels Updated", value=str(len(result.updated_channels)), inline=True
        )
        embed.add_field(
            name="Channels Skipped", value=str(len(result.skipped_channels)), inline=True
        )
        embed.add_field(
            name="Extra Channels", value=str(len(result.extra_channels)), inline=True
        )

        # Add detailed lists
        self._add_channel_list_field(embed, result.created_channels, "New")
        self._add_channel_list_field(embed, result.updated_channels, "Updated")

        if result.extra_channels:
            channel_list = "\n".join(
                [f"• {channel.mention} (not in YAML)" for channel in result.extra_channels]
            )
            embed.add_field(
                name="Extra Channels (Not in YAML)",
                value=channel_list,
                inline=False
            )

        return embed

    @commands.command(name="createchannel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx: commands.Context) -> None:
        """Create a channel based on properties defined in a YAML file."""
        yaml_path = "/home/user/Projects/gitcord-template/community/off-topic.yaml"
        await self._create_single_channel(ctx, yaml_path)

    @commands.command(name="createcategory")
    @commands.has_permissions(manage_channels=True)
    async def createcategory(self, ctx: commands.Context) -> None:
        """Create a category and its channels based on properties defined in a YAML file."""
        guild = self._ensure_guild(ctx)
        if not guild:
            await self.send_error(ctx, "❌ Error", "Guild not found")
            return

        yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            result = await self._create_category_common(guild, yaml_path)

            if not result.category:
                await self.send_error(
                    ctx, "❌ Error", "Failed to process category configuration"
                )
                return

            embed = self._create_category_result_embed(result)

            if result.extra_channels:
                embed.add_field(
                    name="Action Required",
                    value="Use the button below to delete extra channels if needed.",
                    inline=False,
                )
                view = DeleteExtraChannelsView(result.extra_channels, self.logger)
                await ctx.send(embed=embed, view=view)
            else:
                await ctx.send(embed=embed)

            self.logger.info(
                "Category '%s' processed: %d created, %d updated, %d skipped, %d extra",
                result.category.name,
                len(result.created_channels),
                len(result.updated_channels),
                len(result.skipped_channels),
                len(result.extra_channels),
            )

        except (discord.DiscordException, OSError) as e:
            self.logger.error("Unexpected error in createcategory command: %s", e)
            await self.send_error(
                ctx, "❌ Unexpected Error", f"An unexpected error occurred: {str(e)}"
            )

    @app_commands.command(
        name="createcategory",
        description="Create a category and its channels from YAML configuration",
    )
    @app_commands.describe(yaml_path="Path to the category YAML file (optional)")
    async def createcategory_slash(
        self, interaction: discord.Interaction, yaml_path: str | None = None
    ) -> None:
        """Slash command to create a category and its channels based on YAML configuration."""
        await interaction.response.defer()

        # Check permissions
        if not self._ensure_permissions(interaction):
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        # Ensure we have a guild
        guild = self._ensure_guild(interaction)
        if not guild:
            embed = create_embed(
                title="❌ Error",
                description="This command can only be used in a server.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        # Use default path if none provided
        if yaml_path is None:
            yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            result = await self._create_category_common(guild, yaml_path)

            if not result.category:
                embed = create_embed(
                    title="❌ Error",
                    description="Failed to process category configuration. "
                    "Please check the YAML file.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            embed = self._create_category_result_embed(result)

            # Add delete button if there are extra channels
            if result.extra_channels:
                delete_view = DeleteExtraChannelsView(result.extra_channels, self.logger)
                await interaction.followup.send(embed=embed, view=delete_view)
            else:
                await interaction.followup.send(embed=embed)

            self.logger.info(
                "Category '%s' processed: %d created, %d updated, %d skipped, %d extra",
                result.category.name,
                len(result.created_channels),
                len(result.updated_channels),
                len(result.skipped_channels),
                len(result.extra_channels),
            )

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create categories or channels "
                "in this server.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            self.logger.error("Permission error in createcategory slash command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            self.logger.error("Discord HTTP error in createcategory slash command: %s", e)
        except (discord.DiscordException, OSError) as e:
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            self.logger.error("Unexpected error in createcategory slash command: %s", e)


async def setup(bot: commands.Bot) -> None:
    """Set up the Channels cog."""
    await bot.add_cog(Channels(bot))
