"""
General commands cog for GitCord bot.
Contains basic utility commands.
"""

import re
from typing import Optional

import discord
import requests
import yaml
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import format_latency, create_embed, parse_channel_config
from ..utils.logger import main_logger as logger
from ..views import DeleteExtraChannelsView
from ..constants.paths import CATEGORY_YAML_PATH, OFFTOPIC_YAML_PATH, TEMPLATE_DIR
from ..constants.messages import (
    ERR_FILE_NOT_FOUND,
    ERR_INVALID_YAML,
    ERR_INVALID_CONFIG,
    ERR_INVALID_CHANNEL_TYPE,
    ERR_DISCORD_API,
    ERR_UNEXPECTED,
    ERR_FETCH_ERROR,
    SUCCESS_CATEGORY_CREATED,
    SUCCESS_CHANNEL_CREATED,
    SUCCESS_CATEGORY_UPDATED,
    SUCCESS_COMMANDS_SYNCED,
    HELP_DOCS,
    HELP_COMMANDS,
    HELP_SLASH_COMMANDS,
    HELP_LINKS,
    HELP_FOOTER,
)
from ..constants.permissions import (
    ERR_ADMIN_REQUIRED,
    ERR_MANAGE_CHANNELS_REQUIRED,
    ERR_BOT_MISSING_PERMS,
)


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the General cog."""
        self.bot = bot
        logger.info("General cog loaded")

    @commands.command(name="fetchurl")
    @commands.has_permissions(administrator=True)
    async def fetchurl_prefix(self, ctx: commands.Context, url: str) -> None:
        """Prefix command to fetch text content from a URL."""
        try:
            # Validate URL format
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Send initial response
            await ctx.send("🔄 Fetching content from URL...")

            # Fetch the webpage
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove excessive whitespace
            text = re.sub(r"\s+", " ", text)

            # Limit text length to Discord's message limit (2000 characters)
            if len(text) > 1900:  # Leave some room for formatting
                text = text[:1900] + "...\n\n*Content truncated due to length limits*"

            if not text.strip():
                embed = create_embed(
                    title="❌ No Content Found",
                    description="No readable text content was found on the provided URL.",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}",
            )

            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            embed = create_embed(
                title="❌ Fetch Error",
                description=ERR_FETCH_ERROR.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        except discord.DiscordException as e:
            logger.error("Discord error in fetchurl command: %s", e)
            await ctx.send("A Discord error occurred.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in fetchurl command: %s", e)
            embed = create_embed(
                title="❌ Unexpected Error",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @fetchurl_prefix.error
    async def fetchurl_prefix_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle errors for the fetchurl prefix command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description=ERR_ADMIN_REQUIRED,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in fetchurl prefix command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @app_commands.command(
        name="fetchurl", description="Fetch and display text content from a URL"
    )
    @app_commands.describe(url="The URL to fetch text content from")
    @app_commands.checks.has_permissions(administrator=True)
    async def fetchurl(self, interaction: discord.Interaction, url: str) -> None:
        """Slash command to fetch text content from a URL."""
        await interaction.response.defer()

        try:
            # Validate URL format
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Fetch the webpage
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove excessive whitespace
            text = re.sub(r"\s+", " ", text)

            # Limit text length to Discord's message limit (2000 characters)
            if len(text) > 1900:  # Leave some room for formatting
                text = text[:1900] + "...\n\n*Content truncated due to length limits*"

            if not text.strip():
                embed = create_embed(
                    title="❌ No Content Found",
                    description="No readable text content was found on the provided URL.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}",
            )

            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException as e:
            embed = create_embed(
                title="❌ Fetch Error",
                description=ERR_FETCH_ERROR.format(error=str(e)),
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
        except discord.DiscordException as e:
            logger.error("Discord error in fetchurl command: %s", e)
            await interaction.followup.send("A Discord error occurred.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in fetchurl command: %s", e)
            embed = create_embed(
                title="❌ Unexpected Error",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)

    @fetchurl.error
    async def fetchurl_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle errors for the fetchurl slash command."""
        if isinstance(error, app_commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description=ERR_ADMIN_REQUIRED,
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            logger.error("Error in fetchurl slash command: %s", error)
            embed = create_embed(
                title="❌ Error",
                description=f"An error occurred: {error}",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="slashping", description="Check bot latency (slash)")
    async def slashping(self, interaction: discord.Interaction) -> None:
        """Slash command to check bot latency."""
        latency = format_latency(self.bot.latency)
        embed = create_embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}**",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="synccommands", description="Manually sync slash commands"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def synccommands(self, interaction: discord.Interaction) -> None:
        """Synchronize application commands for this guild."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                SUCCESS_COMMANDS_SYNCED.format(count=len(synced)), ephemeral=True
            )
            logger.info(
                "Manually synced %d command(s) in guild: %s",
                len(synced),
                interaction.guild.name if interaction.guild else "N/A",
            )
        except discord.DiscordException as e:
            logger.error("Failed to sync commands: %s", e)
            await interaction.followup.send(
                ERR_DISCORD_API.format(error=str(e)), ephemeral=True
            )

    @commands.command(name="synccommands")
    @commands.has_permissions(administrator=True)
    async def synccommands_prefix(self, ctx: commands.Context) -> None:
        """Prefix command to manually sync slash commands."""
        try:
            # Send initial response
            await ctx.send("🔄 Syncing slash commands...")

            synced = await self.bot.tree.sync(guild=ctx.guild)

            embed = create_embed(
                title="✅ Commands Synced",
                description=SUCCESS_COMMANDS_SYNCED.format(count=len(synced)),
                color=discord.Color.green(),
            )

            await ctx.send(embed=embed)

            logger.info(
                "Manually synced %d command(s) in guild: %s via prefix command",
                len(synced),
                ctx.guild.name if ctx.guild else "N/A",
            )
        except discord.DiscordException as e:
            embed = create_embed(
                title="❌ Sync Failed",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Failed to sync commands via prefix command: %s", e)

    @synccommands_prefix.error
    async def synccommands_prefix_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle errors for the synccommands prefix command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description=ERR_ADMIN_REQUIRED,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in synccommands prefix command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @app_commands.command(
        name="createcategory",
        description="Create a category and its channels from YAML configuration",
    )
    @app_commands.describe(yaml_path="Path to the category YAML file (optional)")
    async def createcategory_slash(
        self, interaction: discord.Interaction, yaml_path: Optional[str] = None
    ) -> None:
        """Slash command to create a category and its channels based on YAML configuration."""
        await interaction.response.defer()

        # Use default path if none provided
        if not yaml_path:
            yaml_path = CATEGORY_YAML_PATH

        try:
            # Ensure interaction.guild and interaction.user are present
            if not interaction.guild or not isinstance(
                interaction.user, discord.Member
            ):
                embed = create_embed(
                    title="❌ Permission Denied",
                    description=ERR_MANAGE_CHANNELS_REQUIRED,
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            # Check if the user has permission to manage channels
            if not interaction.user.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description=ERR_MANAGE_CHANNELS_REQUIRED,
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, "r", encoding="utf-8") as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=ERR_FILE_NOT_FOUND.format(path=yaml_path),
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=ERR_INVALID_YAML.format(error=str(e)),
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            # Validate required fields
            required_fields = ["name", "type", "channels"]
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=ERR_INVALID_CONFIG.format(field=field),
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed)
                    return

            # Check if category already exists
            existing_category = None
            if interaction.guild:
                existing_category = discord.utils.get(
                    interaction.guild.categories, name=category_config["name"]
                )
            if existing_category:
                # Category exists, check for differences and apply updates

                updated_channels = []
                created_channels = []
                skipped_channels = []
                extra_channels = []

                # Get all channels that should exist according to YAML
                yaml_channel_names = set()
                for channel_name in category_config["channels"]:
                    try:
                        channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"
                        channel_config = parse_channel_config(channel_yaml_path)
                        yaml_channel_names.add(channel_config["name"])
                    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                        logger.error(
                            "Failed to parse channel '%s' from YAML: %s",
                            channel_name,
                            e,
                        )

                # Check for channels that exist in Discord but not in YAML
                for existing_channel in existing_category.channels:
                    if existing_channel.name not in yaml_channel_names:
                        extra_channels.append(existing_channel)
                        logger.info(
                            "Found extra channel '%s' in category '%s' (not in YAML)",
                            existing_channel.name,
                            category_config["name"],
                        )

                # Check for category position differences
                category_updated = False
                if existing_category.position != category_config.get("position", 0):
                    try:
                        await existing_category.edit(
                            position=category_config.get("position", 0)
                        )
                        category_updated = True
                        logger.info(
                            "Updated category '%s' position from %d to %d",
                            category_config["name"],
                            existing_category.position,
                            category_config.get("position", 0),
                        )
                    except (discord.Forbidden, discord.HTTPException) as e:
                        logger.error("Failed to update category position: %s", e)

                # Process channels in the category
                for channel_name in category_config["channels"]:
                    try:
                        # Construct path to individual channel YAML file
                        channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"

                        # Parse individual channel configuration
                        channel_config = parse_channel_config(channel_yaml_path)

                        # Check if channel already exists in the category
                        existing_channel = discord.utils.get(
                            existing_category.channels, name=channel_config["name"]
                        )

                        if existing_channel:
                            # Channel exists, check for differences and update
                            channel_updated = False
                            update_kwargs = {}
                            # Only check topic if TextChannel
                            if isinstance(existing_channel, discord.TextChannel):
                                if existing_channel.topic != channel_config.get(
                                    "topic", ""
                                ):
                                    update_kwargs["topic"] = channel_config.get(
                                        "topic", ""
                                    )
                                    channel_updated = True
                            # Only check nsfw if TextChannel or VoiceChannel
                            if hasattr(
                                existing_channel, "nsfw"
                            ) and existing_channel.nsfw != channel_config.get(
                                "nsfw", False
                            ):
                                update_kwargs["nsfw"] = channel_config.get(
                                    "nsfw", False
                                )
                                channel_updated = True
                            # Only check position if attribute exists
                            if (
                                hasattr(existing_channel, "position")
                                and "position" in channel_config
                                and existing_channel.position
                                != channel_config["position"]
                            ):
                                update_kwargs["position"] = channel_config["position"]
                                channel_updated = True
                            if channel_updated:
                                try:
                                    await existing_channel.edit(**update_kwargs)
                                    updated_channels.append(existing_channel)
                                    logger.info(
                                        "Updated channel '%s' in category '%s'",
                                        channel_config["name"],
                                        category_config["name"],
                                    )
                                except (discord.Forbidden, discord.HTTPException) as e:
                                    logger.error(
                                        "Failed to update channel '%s': %s",
                                        channel_config["name"],
                                        e,
                                    )
                                    skipped_channels.append(channel_config["name"])
                            else:
                                skipped_channels.append(channel_config["name"])
                                logger.info(
                                    "Channel '%s' in category '%s' is already up to date",
                                    channel_config["name"],
                                    category_config["name"],
                                )
                        else:
                            # Channel doesn't exist, create it
                            try:
                                channel_kwargs = {
                                    "name": channel_config["name"],
                                    "category": existing_category,
                                    "topic": (
                                        channel_config.get("topic", "")
                                        if channel_config["type"].lower() == "text"
                                        else None
                                    ),
                                    "nsfw": (
                                        channel_config.get("nsfw", False)
                                        if channel_config["type"].lower()
                                        in ("text", "voice")
                                        else None
                                    ),
                                }
                                if "position" in channel_config:
                                    channel_kwargs["position"] = channel_config[
                                        "position"
                                    ]
                                # Remove None values
                                channel_kwargs = {
                                    k: v
                                    for k, v in channel_kwargs.items()
                                    if v is not None
                                }
                                if channel_config["type"].lower() == "text":
                                    new_channel = (
                                        await interaction.guild.create_text_channel(
                                            **channel_kwargs
                                        )
                                    )
                                elif channel_config["type"].lower() == "voice":
                                    new_channel = (
                                        await interaction.guild.create_voice_channel(
                                            **channel_kwargs
                                        )
                                    )
                                else:
                                    logger.warning(
                                        "Skipping channel '%s': Invalid type '%s'",
                                        channel_name,
                                        channel_config["type"],
                                    )
                                    skipped_channels.append(channel_config["name"])
                                    continue
                                created_channels.append(new_channel)
                                logger.info(
                                    "Created new channel '%s' in existing category '%s'",
                                    channel_config["name"],
                                    category_config["name"],
                                )
                            except (
                                ValueError,
                                FileNotFoundError,
                                discord.Forbidden,
                                discord.HTTPException,
                            ) as e:
                                logger.error(
                                    "Failed to create channel '%s': %s", channel_name, e
                                )
                                skipped_channels.append(channel_config["name"])
                    except (
                        ValueError,
                        FileNotFoundError,
                        discord.Forbidden,
                        discord.HTTPException,
                    ) as e:
                        logger.error(
                            "Failed to process channel '%s': %s", channel_name, e
                        )
                        skipped_channels.append(channel_name)
                        continue
                # Create result embed
                embed = create_embed(
                    title=SUCCESS_CATEGORY_UPDATED,
                    description=f"Successfully processed category: **{existing_category.name}**",
                    color=discord.Color.green(),
                )

                # Add fields
                embed.add_field(
                    name="Category", value=existing_category.mention, inline=True
                )
                if category_updated:
                    embed.add_field(
                        name="Category Updated", value="✅ Position", inline=True
                    )
                else:
                    embed.add_field(
                        name="Category Updated", value="❌ No changes", inline=True
                    )

                embed.add_field(
                    name="Channels Created",
                    value=str(len(created_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Channels Updated",
                    value=str(len(updated_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Channels Skipped",
                    value=str(len(skipped_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Extra Channels", value=str(len(extra_channels)), inline=True
                )

                if created_channels:
                    channel_list = "\n".join(
                        [f"• {channel.mention} (new)" for channel in created_channels]
                    )
                    embed.add_field(
                        name="New Channels", value=channel_list, inline=False
                    )

                if updated_channels:
                    channel_list = "\n".join(
                        [
                            f"• {channel.mention} (updated)"
                            for channel in updated_channels
                        ]
                    )
                    embed.add_field(
                        name="Updated Channels", value=channel_list, inline=False
                    )

                if extra_channels:
                    channel_list = "\n".join(
                        [
                            f"• {channel.mention} (not in YAML)"
                            for channel in extra_channels
                        ]
                    )
                    embed.add_field(
                        name="Extra Channels (Not in YAML)",
                        value=channel_list,
                        inline=False,
                    )

                # Add delete button if there are extra channels
                if extra_channels:
                    delete_view = DeleteExtraChannelsView(
                        extra_channels, existing_category.name
                    )
                    await interaction.followup.send(embed=embed, view=delete_view)
                else:
                    await interaction.followup.send(embed=embed)

                logger.info(
                    "Category '%s' processed: %d created, %d updated, %d skipped, %d extra",
                    category_config["name"],
                    len(created_channels),
                    len(updated_channels),
                    len(skipped_channels),
                    len(extra_channels),
                )
                return

            # Create the category (original logic for new categories)
            if interaction.guild:
                category_kwargs = {
                    "name": category_config["name"],
                    "position": category_config.get("position", 0),
                }
                new_category = await interaction.guild.create_category(
                    **category_kwargs
                )
                created_channels = []

                # Create channels within the category
                for channel_name in category_config["channels"]:
                    try:
                        # Construct path to individual channel YAML file
                        channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"

                        # Parse individual channel configuration
                        channel_config = parse_channel_config(channel_yaml_path)

                        # Check if channel already exists in the category
                        existing_channel = discord.utils.get(
                            new_category.channels, name=channel_config["name"]
                        )
                        if existing_channel:
                            logger.warning(
                                "Channel '%s' already exists in category '%s', skipping",
                                channel_config["name"],
                                category_config["name"],
                            )
                            continue

                        # Prepare channel creation parameters
                        channel_kwargs = {
                            "name": channel_config["name"],
                            "category": new_category,
                            "topic": (
                                channel_config.get("topic", "")
                                if channel_config["type"].lower() == "text"
                                else None
                            ),
                            "nsfw": (
                                channel_config.get("nsfw", False)
                                if channel_config["type"].lower() in ("text", "voice")
                                else None
                            ),
                        }

                        # Set position if specified
                        if "position" in channel_config:
                            channel_kwargs["position"] = channel_config["position"]

                        # Create the channel based on type
                        if channel_config["type"].lower() == "text":
                            new_channel = await interaction.guild.create_text_channel(
                                **channel_kwargs
                            )
                        elif channel_config["type"].lower() == "voice":
                            new_channel = await interaction.guild.create_voice_channel(
                                **channel_kwargs
                            )
                        else:
                            logger.warning(
                                "Skipping channel '%s': Invalid type '%s'",
                                channel_name,
                                channel_config["type"],
                            )
                            continue

                        created_channels.append(new_channel)
                        logger.info(
                            "Channel '%s' created successfully in category '%s'",
                            channel_config["name"],
                            category_config["name"],
                        )

                    except (
                        ValueError,
                        FileNotFoundError,
                        discord.Forbidden,
                        discord.HTTPException,
                    ) as e:
                        logger.error(
                            "Failed to create channel '%s': %s", channel_name, e
                        )
                        continue

                # Create success embed
                embed = create_embed(
                    title=SUCCESS_CATEGORY_CREATED,
                    description=f"Successfully created category: **{new_category.name}**",
                    color=discord.Color.green(),
                )

                # Add fields
                embed.add_field(
                    name="Category Name", value=new_category.name, inline=True
                )
                embed.add_field(
                    name="Category Type", value=category_config["type"], inline=True
                )
                embed.add_field(
                    name="Position",
                    value=category_config.get("position", 0),
                    inline=True,
                )
                embed.add_field(
                    name="Channels Created",
                    value=f"{len(created_channels)}/{len(category_config['channels'])}",
                    inline=False,
                )

                if created_channels:
                    channel_list = "\n".join(
                        [f"• {channel.mention}" for channel in created_channels]
                    )
                    embed.add_field(
                        name="Created Channels", value=channel_list, inline=False
                    )

                await interaction.followup.send(embed=embed)
                logger.info(
                    "Category '%s' with %d channels created successfully by %s",
                    category_config["name"],
                    len(created_channels),
                    interaction.user,
                )

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description=ERR_BOT_MISSING_PERMS,
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            logger.error("Permission error in createcategory slash command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=ERR_DISCORD_API.format(error=str(e)),
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            logger.error("Discord HTTP error in createcategory slash command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            logger.error("Unexpected error in createcategory slash command: %s", e)

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context) -> None:
        """Simple hello world command."""
        author = ctx.author if isinstance(ctx.author, discord.Member) else None
        embed = create_embed(
            title="👋 Welcome!",
            description=f"Hello, {ctx.author.mention}! Welcome to GitCord!",
            color=discord.Color.blue(),
            author=author,
        )
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context) -> None:
        """Check bot latency."""
        latency = format_latency(self.bot.latency)
        embed = create_embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}**",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="createchannel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx: commands.Context) -> None:
        """Create a channel based on properties defined in a YAML file."""
        yaml_path = OFFTOPIC_YAML_PATH

        try:
            # Check if the user has permission to manage channels
            if not (
                isinstance(ctx.author, discord.Member)
                and ctx.author.guild_permissions.manage_channels
            ):
                embed = create_embed(
                    title="❌ Permission Denied",
                    description=ERR_MANAGE_CHANNELS_REQUIRED,
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            try:
                channel_config = parse_channel_config(yaml_path)
            except ValueError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=ERR_INVALID_YAML.format(error=str(e)),
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Prepare channel creation parameters
            channel_kwargs = {
                "name": channel_config["name"],
                "topic": (
                    channel_config.get("topic", "")
                    if channel_config["type"].lower() == "text"
                    else None
                ),
                "nsfw": (
                    channel_config.get("nsfw", False)
                    if channel_config["type"].lower() in ("text", "voice")
                    else None
                ),
            }
            if "position" in channel_config:
                channel_kwargs["position"] = channel_config["position"]
            channel_kwargs = {k: v for k, v in channel_kwargs.items() if v is not None}

            # Create the channel based on type
            if ctx.guild:
                if channel_config["type"].lower() == "text":
                    new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
                elif channel_config["type"].lower() == "voice":
                    new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
                else:
                    embed = create_embed(
                        title="❌ Invalid Channel Type",
                        description=ERR_INVALID_CHANNEL_TYPE.format(
                            type=channel_config["type"]
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                embed = create_embed(
                    title="❌ Permission Error",
                    description=ERR_BOT_MISSING_PERMS,
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Create success embed
            embed = create_embed(
                title="✅ Channel Created",
                description=SUCCESS_CHANNEL_CREATED.format(mention=new_channel.mention),
                color=discord.Color.green(),
            )
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
            logger.info(
                "Channel '%s' created successfully by %s",
                channel_config["name"],
                ctx.author,
            )

        except yaml.YAMLError as e:
            embed = create_embed(
                title="❌ YAML Parse Error",
                description=ERR_INVALID_YAML.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("YAML parse error in createchannel command: %s", e)
        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description=ERR_BOT_MISSING_PERMS,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createchannel command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=ERR_DISCORD_API.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createchannel command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createchannel command: %s", e)

    @createchannel.error
    async def createchannel_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle errors for the createchannel command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description=ERR_MANAGE_CHANNELS_REQUIRED,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createchannel command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name="createcategory")
    @commands.has_permissions(manage_channels=True)
    async def createcategory(self, ctx: commands.Context) -> None:
        """Create a category and its channels based on properties defined in a YAML file."""
        yaml_path = CATEGORY_YAML_PATH

        try:
            # Check if the user has permission to manage channels
            if not (
                isinstance(ctx.author, discord.Member)
                and ctx.author.guild_permissions.manage_channels
            ):
                embed = create_embed(
                    title="❌ Permission Denied",
                    description=ERR_MANAGE_CHANNELS_REQUIRED,
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, "r", encoding="utf-8") as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=ERR_FILE_NOT_FOUND.format(path=yaml_path),
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=ERR_INVALID_YAML.format(error=str(e)),
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Validate required fields
            required_fields = ["name", "type", "channels"]
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=ERR_INVALID_CONFIG.format(field=field),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=embed)
                    return

            # Check if category already exists
            existing_category = None
            if ctx.guild:
                existing_category = discord.utils.get(
                    ctx.guild.categories, name=category_config["name"]
                )
            if existing_category:
                updated_channels = []
                created_channels = []
                skipped_channels = []
                extra_channels = []
                yaml_channel_names = set()
                for channel_name in category_config["channels"]:
                    try:
                        channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"
                        channel_config = parse_channel_config(channel_yaml_path)
                        yaml_channel_names.add(channel_config["name"])
                    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                        logger.error(
                            "Failed to parse channel '%s' from YAML: %s",
                            channel_name,
                            e,
                        )
                for existing_channel in existing_category.channels:
                    if existing_channel.name not in yaml_channel_names:
                        extra_channels.append(existing_channel)
                        logger.info(
                            "Found extra channel '%s' in category '%s' (not in YAML)",
                            existing_channel.name,
                            category_config["name"],
                        )
                category_updated = False
                if existing_category.position != category_config.get("position", 0):
                    try:
                        await existing_category.edit(
                            position=category_config.get("position", 0)
                        )
                        category_updated = True
                        logger.info(
                            "Updated category '%s' position from %d to %d",
                            category_config["name"],
                            existing_category.position,
                            category_config.get("position", 0),
                        )
                    except (discord.Forbidden, discord.HTTPException) as e:
                        logger.error("Failed to update category position: %s", e)
                for channel_name in category_config["channels"]:
                    try:
                        channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"
                        channel_config = parse_channel_config(channel_yaml_path)
                        existing_channel = discord.utils.get(
                            existing_category.channels, name=channel_config["name"]
                        )
                        if existing_channel:
                            channel_updated = False
                            update_kwargs = {}
                            if isinstance(existing_channel, discord.TextChannel):
                                if existing_channel.topic != channel_config.get(
                                    "topic", ""
                                ):
                                    update_kwargs["topic"] = channel_config.get(
                                        "topic", ""
                                    )
                                    channel_updated = True
                            if hasattr(
                                existing_channel, "nsfw"
                            ) and existing_channel.nsfw != channel_config.get(
                                "nsfw", False
                            ):
                                update_kwargs["nsfw"] = channel_config.get(
                                    "nsfw", False
                                )
                                channel_updated = True
                            if (
                                hasattr(existing_channel, "position")
                                and "position" in channel_config
                                and existing_channel.position
                                != channel_config["position"]
                            ):
                                update_kwargs["position"] = channel_config["position"]
                                channel_updated = True
                            if channel_updated:
                                try:
                                    await existing_channel.edit(**update_kwargs)
                                    updated_channels.append(existing_channel)
                                    logger.info(
                                        "Updated channel '%s' in category '%s'",
                                        channel_config["name"],
                                        category_config["name"],
                                    )
                                except (discord.Forbidden, discord.HTTPException) as e:
                                    logger.error(
                                        "Failed to update channel '%s': %s",
                                        channel_config["name"],
                                        e,
                                    )
                                    skipped_channels.append(channel_config["name"])
                            else:
                                skipped_channels.append(channel_config["name"])
                                logger.info(
                                    "Channel '%s' in category '%s' is already up to date",
                                    channel_config["name"],
                                    category_config["name"],
                                )
                        else:
                            try:
                                channel_kwargs = {
                                    "name": channel_config["name"],
                                    "category": existing_category,
                                    "topic": (
                                        channel_config.get("topic", "")
                                        if channel_config["type"].lower() == "text"
                                        else None
                                    ),
                                    "nsfw": (
                                        channel_config.get("nsfw", False)
                                        if channel_config["type"].lower()
                                        in ("text", "voice")
                                        else None
                                    ),
                                }
                                if "position" in channel_config:
                                    channel_kwargs["position"] = channel_config[
                                        "position"
                                    ]
                                channel_kwargs = {
                                    k: v
                                    for k, v in channel_kwargs.items()
                                    if v is not None
                                }
                                if channel_config["type"].lower() == "text":
                                    new_channel = await ctx.guild.create_text_channel(
                                        **channel_kwargs
                                    )
                                elif channel_config["type"].lower() == "voice":
                                    new_channel = await ctx.guild.create_voice_channel(
                                        **channel_kwargs
                                    )
                                else:
                                    logger.warning(
                                        "Skipping channel '%s': Invalid type '%s'",
                                        channel_name,
                                        channel_config["type"],
                                    )
                                    skipped_channels.append(channel_config["name"])
                                    continue
                                created_channels.append(new_channel)
                                logger.info(
                                    "Created new channel '%s' in existing category '%s'",
                                    channel_config["name"],
                                    category_config["name"],
                                )
                            except (
                                ValueError,
                                FileNotFoundError,
                                discord.Forbidden,
                                discord.HTTPException,
                            ) as e:
                                logger.error(
                                    "Failed to create channel '%s': %s", channel_name, e
                                )
                                skipped_channels.append(channel_config["name"])
                    except (
                        ValueError,
                        FileNotFoundError,
                        discord.Forbidden,
                        discord.HTTPException,
                    ) as e:
                        logger.error(
                            "Failed to process channel '%s': %s", channel_name, e
                        )
                        skipped_channels.append(channel_name)
                        continue
                embed = create_embed(
                    title=SUCCESS_CATEGORY_UPDATED,
                    description=f"Successfully processed category: **{existing_category.name}**",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name="Category", value=existing_category.mention, inline=True
                )
                if category_updated:
                    embed.add_field(
                        name="Category Updated", value="✅ Position", inline=True
                    )
                else:
                    embed.add_field(
                        name="Category Updated", value="❌ No changes", inline=True
                    )
                embed.add_field(
                    name="Channels Created",
                    value=str(len(created_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Channels Updated",
                    value=str(len(updated_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Channels Skipped",
                    value=str(len(skipped_channels)),
                    inline=True,
                )
                embed.add_field(
                    name="Extra Channels", value=str(len(extra_channels)), inline=True
                )
                if created_channels:
                    channel_list = "\n".join(
                        [f"• {channel.mention} (new)" for channel in created_channels]
                    )
                    embed.add_field(
                        name="New Channels", value=channel_list, inline=False
                    )
                if updated_channels:
                    channel_list = "\n".join(
                        [
                            f"• {channel.mention} (updated)"
                            for channel in updated_channels
                        ]
                    )
                    embed.add_field(
                        name="Updated Channels", value=channel_list, inline=False
                    )
                if extra_channels:
                    channel_list = "\n".join(
                        [
                            f"• {channel.mention} (not in YAML)"
                            for channel in extra_channels
                        ]
                    )
                    embed.add_field(
                        name="Extra Channels (Not in YAML)",
                        value=channel_list,
                        inline=False,
                    )
                if extra_channels:
                    delete_view = DeleteExtraChannelsView(
                        extra_channels, existing_category.name
                    )
                    await ctx.send(embed=embed, view=delete_view)
                else:
                    await ctx.send(embed=embed)
                logger.info(
                    "Category '%s' processed: %d created, %d updated, %d skipped, %d extra",
                    category_config["name"],
                    len(created_channels),
                    len(updated_channels),
                    len(skipped_channels),
                    len(extra_channels),
                )
                return
            if ctx.guild is None:
                embed = create_embed(
                    title="❌ Error",
                    description="This command can only be used in a server.",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            category_kwargs = {
                "name": category_config["name"],
                "position": category_config.get("position", 0),
            }
            new_category = await ctx.guild.create_category(**category_kwargs)
            created_channels = []
            for channel_name in category_config["channels"]:
                try:
                    channel_yaml_path = f"{TEMPLATE_DIR}/{channel_name}.yaml"
                    channel_config = parse_channel_config(channel_yaml_path)
                    existing_channel = discord.utils.get(
                        new_category.channels, name=channel_config["name"]
                    )
                    if existing_channel:
                        logger.warning(
                            "Channel '%s' already exists in category '%s', skipping",
                            channel_config["name"],
                            category_config["name"],
                        )
                        continue
                    channel_kwargs = {
                        "name": channel_config["name"],
                        "category": new_category,
                        "topic": (
                            channel_config.get("topic", "")
                            if channel_config["type"].lower() == "text"
                            else None
                        ),
                        "nsfw": (
                            channel_config.get("nsfw", False)
                            if channel_config["type"].lower() in ("text", "voice")
                            else None
                        ),
                    }
                    if "position" in channel_config:
                        channel_kwargs["position"] = channel_config["position"]
                    channel_kwargs = {
                        k: v for k, v in channel_kwargs.items() if v is not None
                    }
                    if channel_config["type"].lower() == "text":
                        new_channel = await ctx.guild.create_text_channel(
                            **channel_kwargs
                        )
                    elif channel_config["type"].lower() == "voice":
                        new_channel = await ctx.guild.create_voice_channel(
                            **channel_kwargs
                        )
                    else:
                        logger.warning(
                            "Skipping channel '%s': Invalid type '%s'",
                            channel_name,
                            channel_config["type"],
                        )
                        continue
                    created_channels.append(new_channel)
                    logger.info(
                        "Channel '%s' created successfully in category '%s'",
                        channel_config["name"],
                        category_config["name"],
                    )
                except (
                    ValueError,
                    FileNotFoundError,
                    discord.Forbidden,
                    discord.HTTPException,
                ) as e:
                    logger.error("Failed to create channel '%s': %s", channel_name, e)
                    continue
            embed = create_embed(
                title=SUCCESS_CATEGORY_CREATED,
                description=f"Successfully created category: **{new_category.name}**",
                color=discord.Color.green(),
            )
            embed.add_field(name="Category Name", value=new_category.name, inline=True)
            embed.add_field(
                name="Category Type", value=category_config["type"], inline=True
            )
            embed.add_field(
                name="Position",
                value=category_config.get("position", 0),
                inline=True,
            )
            embed.add_field(
                name="Channels Created",
                value=f"{len(created_channels)}/{len(category_config['channels'])}",
                inline=False,
            )
            if created_channels:
                channel_list = "\n".join(
                    [f"• {channel.mention}" for channel in created_channels]
                )
                embed.add_field(
                    name="Created Channels", value=channel_list, inline=False
                )
            await ctx.send(embed=embed)
            logger.info(
                "Category '%s' with %d channels created successfully by %s",
                category_config["name"],
                len(created_channels),
                ctx.author,
            )

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description=ERR_BOT_MISSING_PERMS,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createcategory command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=ERR_DISCORD_API.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createcategory command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=ERR_UNEXPECTED.format(error=str(e)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createcategory command: %s", e)

    @createcategory.error
    async def createcategory_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle errors for the createcategory command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description=ERR_MANAGE_CHANNELS_REQUIRED,
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createcategory command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context) -> None:
        """Prefix command to show help information and link to the wiki."""
        author = ctx.author if isinstance(ctx.author, discord.Member) else None
        embed = create_embed(
            title="🤖 GitCord Help",
            description="Welcome to GitCord! Here's how to get help and learn more about the bot.",
            color=discord.Color.blue(),
            author=author,
        )

        embed.add_field(name="📚 Documentation", value=HELP_DOCS, inline=False)

        embed.add_field(name="🔧 Available Commands", value=HELP_COMMANDS, inline=False)

        embed.add_field(
            name="⚡ Slash Commands", value=HELP_SLASH_COMMANDS, inline=False
        )

        embed.add_field(name="🔗 Quick Links", value=HELP_LINKS, inline=False)

        embed.set_footer(text=HELP_FOOTER)

        await ctx.send(embed=embed)

    @app_commands.command(
        name="help", description="Show help information and link to the wiki"
    )
    async def help_slash(self, interaction: discord.Interaction) -> None:
        """Slash command to show help information and link to the wiki."""
        author = (
            interaction.user if isinstance(interaction.user, discord.Member) else None
        )
        embed = create_embed(
            title="🤖 GitCord Help",
            description="Welcome to GitCord! Here's how to get help and learn more about the bot.",
            color=discord.Color.blue(),
            author=author,
        )

        embed.add_field(name="📚 Documentation", value=HELP_DOCS, inline=False)

        embed.add_field(name="🔧 Available Commands", value=HELP_COMMANDS, inline=False)

        embed.add_field(
            name="⚡ Slash Commands", value=HELP_SLASH_COMMANDS, inline=False
        )

        embed.add_field(name="🔗 Quick Links", value=HELP_LINKS, inline=False)

        embed.set_footer(text=HELP_FOOTER)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Set up the General cog."""
    await bot.add_cog(General(bot))
