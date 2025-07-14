"""
General commands cog for GitCord bot.
Contains basic utility commands.
"""

import re

import discord
import requests
import yaml
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import format_latency, create_embed, parse_channel_config
from ..utils.logger import main_logger as logger


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the General cog."""
        self.bot = bot
        logger.info("General cog loaded")

    @commands.command(name='fetchurl')
    async def fetchurl_prefix(self, ctx: commands.Context, url: str) -> None:
        """Prefix command to fetch text content from a URL."""
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Send initial response
            await ctx.send("🔄 Fetching content from URL...")

            # Fetch the webpage
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)

            # Limit text length to Discord's message limit (2000 characters)
            if len(text) > 1900:  # Leave some room for formatting
                text = text[:1900] + "...\n\n*Content truncated due to length limits*"

            if not text.strip():
                embed = create_embed(
                    title="❌ No Content Found",
                    description="No readable text content was found on the provided URL.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}"
            )

            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            embed = create_embed(
                title="❌ Fetch Error",
                description=f"Failed to fetch content from the URL: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except discord.DiscordException as e:
            logger.error("Discord error in fetchurl command: %s", e)
            await ctx.send("A Discord error occurred.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in fetchurl command: %s", e)
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="fetchurl", description="Fetch and display text content from a URL")
    @app_commands.describe(url="The URL to fetch text content from")
    async def fetchurl(self, interaction: discord.Interaction, url: str) -> None:
        """Slash command to fetch text content from a URL."""
        await interaction.response.defer()

        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Fetch the webpage
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)

            # Limit text length to Discord's message limit (2000 characters)
            if len(text) > 1900:  # Leave some room for formatting
                text = text[:1900] + "...\n\n*Content truncated due to length limits*"

            if not text.strip():
                embed = create_embed(
                    title="❌ No Content Found",
                    description="No readable text content was found on the provided URL.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}"
            )

            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException as e:
            embed = create_embed(
                title="❌ Fetch Error",
                description=f"Failed to fetch content from the URL: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
        except discord.DiscordException as e:
            logger.error("Discord error in fetchurl command: %s", e)
            await interaction.followup.send("A Discord error occurred.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in fetchurl command: %s", e)
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="slashping", description="Check bot latency (slash)")
    async def slashping(self, interaction: discord.Interaction) -> None:
        """Slash command to check bot latency."""
        latency = format_latency(self.bot.latency)
        embed = create_embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="createcategory", description="Create a category and its channels from YAML configuration")
    @app_commands.describe(yaml_path="Path to the category YAML file (optional)")
    async def createcategory_slash(self, interaction: discord.Interaction, yaml_path: str = None) -> None:
        """Slash command to create a category and its channels based on YAML configuration."""
        await interaction.response.defer()

        # Use default path if none provided
        if yaml_path is None:
            yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            # Check if the user has permission to manage channels
            if not interaction.user.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=f"Category YAML file not found at: {yaml_path}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=f"Failed to parse YAML file: {str(e)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Validate required fields
            required_fields = ['name', 'type', 'channels']
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=f"Missing required field: {field}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return

            # Create the category
            category_kwargs = {
                'name': category_config['name'],
                'position': category_config.get('position', 0)
            }

            new_category = await interaction.guild.create_category(**category_kwargs)
            created_channels = []

            # Create channels within the category
            for channel_name in category_config['channels']:
                try:
                    # Construct path to individual channel YAML file
                    channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                    
                    # Parse individual channel configuration
                    channel_config = parse_channel_config(channel_yaml_path)
                    
                    # Prepare channel creation parameters
                    channel_kwargs = {
                        'name': channel_config['name'],
                        'category': new_category,
                        'topic': channel_config.get('topic', ''),
                        'nsfw': channel_config.get('nsfw', False)
                    }

                    # Set position if specified
                    if 'position' in channel_config:
                        channel_kwargs['position'] = channel_config['position']

                    # Create the channel based on type
                    if channel_config['type'].lower() == 'text':
                        new_channel = await interaction.guild.create_text_channel(**channel_kwargs)
                    elif channel_config['type'].lower() == 'voice':
                        new_channel = await interaction.guild.create_voice_channel(**channel_kwargs)
                    else:
                        logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                     channel_name, channel_config['type'])
                        continue

                    created_channels.append(new_channel)
                    logger.info("Channel '%s' created successfully in category '%s'", 
                              channel_config['name'], category_config['name'])

                except Exception as e:
                    logger.error("Failed to create channel '%s': %s", channel_name, e)
                    continue

            # Create success embed
            embed = create_embed(
                title="✅ Category Created",
                description=f"Successfully created category: **{new_category.name}**",
                color=discord.Color.green()
            )

            # Add fields
            embed.add_field(name="Category Name", value=new_category.name, inline=True)
            embed.add_field(name="Category Type", value=category_config['type'], inline=True)
            embed.add_field(name="Position", value=category_config.get('position', 0), inline=True)
            embed.add_field(name="Channels Created", value=f"{len(created_channels)}/{len(category_config['channels'])}", inline=False)

            if created_channels:
                channel_list = "\n".join([f"• {channel.mention}" for channel in created_channels])
                embed.add_field(name="Created Channels", value=channel_list, inline=False)

            await interaction.followup.send(embed=embed)
            logger.info("Category '%s' with %d channels created successfully by %s", 
                       category_config['name'], len(created_channels), interaction.user)

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create categories or channels in this server.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Permission error in createcategory slash command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Discord HTTP error in createcategory slash command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Unexpected error in createcategory slash command: %s", e)

    @commands.command(name='hello')
    async def hello(self, ctx: commands.Context) -> None:
        """Simple hello world command."""
        embed = create_embed(
            title="👋 Welcome!",
            description=f"Hello, {ctx.author.mention}! Welcome to GitCord!",
            color=discord.Color.blue(),
            author=ctx.author
        )
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping_prefix(self, ctx: commands.Context) -> None:
        """Check bot latency."""
        latency = format_latency(self.bot.latency)
        embed = create_embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='createchannel')
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx: commands.Context) -> None:
        """Create a channel based on properties defined in a YAML file."""
        yaml_path = "/home/user/Projects/gitcord-template/community/off-topic.yaml"

        try:
            # Check if the user has permission to manage channels
            if not ctx.author.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            try:
                channel_config = parse_channel_config(yaml_path)
            except ValueError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=str(e),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Prepare channel creation parameters
            channel_kwargs = {
                'name': channel_config['name'],
                'topic': channel_config.get('topic', ''),
                'nsfw': channel_config.get('nsfw', False)
            }

            # Set position if specified
            if 'position' in channel_config:
                channel_kwargs['position'] = channel_config['position']

            # Create the channel based on type
            if channel_config['type'].lower() == 'text':
                new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
            elif channel_config['type'].lower() == 'voice':
                new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
            else:
                embed = create_embed(
                    title="❌ Invalid Channel Type",
                    description=f"Channel type '{channel_config['type']}' is not supported. "
                                "Use 'text' or 'voice'.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Create success embed
            embed = create_embed(
                title="✅ Channel Created",
                description=f"Successfully created channel: {new_channel.mention}",
                color=discord.Color.green()
            )

            # Add fields manually
            embed.add_field(name="Name", value=channel_kwargs['name'], inline=True)
            embed.add_field(name="Type", value=channel_kwargs['type'], inline=True)
            embed.add_field(name="NSFW", value=channel_kwargs['nsfw'], inline=True)
            embed.add_field(name="Topic", value=channel_config.get('topic', 'No topic set'),
                            inline=False)

            await ctx.send(embed=embed)
            logger.info("Channel '%s' created successfully by %s", channel_config['name'],
                        ctx.author)

        except yaml.YAMLError as e:
            embed = create_embed(
                title="❌ YAML Parse Error",
                description=f"Failed to parse YAML file: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("YAML parse error in createchannel command: %s", e)
        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create channels in this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createchannel command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createchannel command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createchannel command: %s", e)

    @createchannel.error
    async def createchannel_error(self, ctx: commands.Context,
                                  error: commands.CommandError) -> None:
        """Handle errors for the createchannel command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createchannel command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name='createcategory')
    @commands.has_permissions(manage_channels=True)
    async def createcategory(self, ctx: commands.Context) -> None:
        """Create a category and its channels based on properties defined in a YAML file."""
        yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            # Check if the user has permission to manage channels
            if not ctx.author.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=f"Category YAML file not found at: {yaml_path}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=f"Failed to parse YAML file: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Validate required fields
            required_fields = ['name', 'type', 'channels']
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=f"Missing required field: {field}",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return

            # Create the category
            category_kwargs = {
                'name': category_config['name'],
                'position': category_config.get('position', 0)
            }

            new_category = await ctx.guild.create_category(**category_kwargs)
            created_channels = []

            # Create channels within the category
            for channel_name in category_config['channels']:
                try:
                    # Construct path to individual channel YAML file
                    channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                    
                    # Parse individual channel configuration
                    channel_config = parse_channel_config(channel_yaml_path)
                    
                    # Prepare channel creation parameters
                    channel_kwargs = {
                        'name': channel_config['name'],
                        'category': new_category,
                        'topic': channel_config.get('topic', ''),
                        'nsfw': channel_config.get('nsfw', False)
                    }

                    # Set position if specified
                    if 'position' in channel_config:
                        channel_kwargs['position'] = channel_config['position']

                    # Create the channel based on type
                    if channel_config['type'].lower() == 'text':
                        new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
                    elif channel_config['type'].lower() == 'voice':
                        new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
                    else:
                        logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                     channel_name, channel_config['type'])
                        continue

                    created_channels.append(new_channel)
                    logger.info("Channel '%s' created successfully in category '%s'", 
                              channel_config['name'], category_config['name'])

                except Exception as e:
                    logger.error("Failed to create channel '%s': %s", channel_name, e)
                    continue

            # Create success embed
            embed = create_embed(
                title="✅ Category Created",
                description=f"Successfully created category: **{new_category.name}**",
                color=discord.Color.green()
            )

            # Add fields
            embed.add_field(name="Category Name", value=new_category.name, inline=True)
            embed.add_field(name="Category Type", value=category_config['type'], inline=True)
            embed.add_field(name="Position", value=category_config.get('position', 0), inline=True)
            embed.add_field(name="Channels Created", value=f"{len(created_channels)}/{len(category_config['channels'])}", inline=False)

            if created_channels:
                channel_list = "\n".join([f"• {channel.mention}" for channel in created_channels])
                embed.add_field(name="Created Channels", value=channel_list, inline=False)

            await ctx.send(embed=embed)
            logger.info("Category '%s' with %d channels created successfully by %s", 
                       category_config['name'], len(created_channels), ctx.author)

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create categories or channels in this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createcategory command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createcategory command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createcategory command: %s", e)

    @createcategory.error
    async def createcategory_error(self, ctx: commands.Context,
                                   error: commands.CommandError) -> None:
        """Handle errors for the createcategory command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createcategory command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Try `!hello` or `!ping`!")
        else:
            logger.error("Command error in %s: %s", ctx.command, error)
            await ctx.send(f"An error occurred: {error}")


async def setup(bot: commands.Bot) -> None:
    """Set up the General cog."""
    await bot.add_cog(General(bot))
