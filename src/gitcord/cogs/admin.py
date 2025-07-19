"""
Administrative commands cog for GitCord bot.
Contains admin-only utility commands.
"""

import re

import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import create_embed
from ..utils.logger import main_logger as logger


class Admin(commands.Cog):
    """Administrative utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Admin cog."""
        self.bot = bot
        logger.info("Admin cog loaded")

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
                description=f"Failed to fetch content from the URL: {str(e)}",
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
                description=f"An unexpected error occurred: {str(e)}",
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
                description="You need the 'Administrator' permission to use this command.",
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
                description=f"Failed to fetch content from the URL: {str(e)}",
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
                description=f"An unexpected error occurred: {str(e)}",
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
                description="You need the 'Administrator' permission to use this command.",
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
                f"Synced {len(synced)} command(s).", ephemeral=True
            )
            logger.info(
                "Manually synced %d command(s) in guild: %s",
                len(synced),
                interaction.guild.name if interaction.guild else "N/A",
            )
        except discord.DiscordException as e:
            logger.error("Failed to sync commands: %s", e)
            await interaction.followup.send(
                f"Failed to sync commands: {e}", ephemeral=True
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
                description=f"Successfully synced **{len(synced)}** command(s) to this guild.",
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
                description=f"Failed to sync commands: {str(e)}",
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
                description="You need the 'Administrator' permission to use this command.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in synccommands prefix command: %s", error)
            await ctx.send(f"An error occurred: {error}")


async def setup(bot: commands.Bot) -> None:
    """Set up the Admin cog."""
    await bot.add_cog(Admin(bot))
