"""
Administrative commands cog for GitCord bot.
Contains admin-only utility commands.
"""

import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from .base_cog import BaseCog
from ..utils.helpers import create_embed, clean_webpage_text


class Admin(BaseCog):
    """Administrative utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Admin cog."""
        super().__init__(bot)
        self.logger.info("Admin cog loaded")

    async def _fetch_url_content(self, url: str) -> str:
        """Fetch and clean content from a URL."""
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

        # Get text content and clean it
        text = soup.get_text()
        return clean_webpage_text(text)

    @commands.command(name="fetchurl")
    @commands.has_permissions(administrator=True)
    async def fetchurl_prefix(self, ctx: commands.Context, url: str) -> None:
        """Prefix command to fetch text content from a URL."""
        try:
            # Send initial response
            await ctx.send("🔄 Fetching content from URL...")

            # Fetch and process content
            text = await self._fetch_url_content(url)

            if not text.strip():
                await self.send_error(
                    ctx,
                    "❌ No Content Found",
                    "No readable text content was found on the provided URL.",
                )
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
            await self.send_error(
                ctx, "❌ Fetch Error", f"Failed to fetch content from the URL: {str(e)}"
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Error in fetchurl command: %s", e)
            await self.send_error(
                ctx, "❌ Unexpected Error", f"An unexpected error occurred: {str(e)}"
            )

    @app_commands.command(name="fetchurl", description="Fetch and display text content from a URL")
    @app_commands.describe(url="The URL to fetch text content from")
    @app_commands.checks.has_permissions(administrator=True)
    async def fetchurl(self, interaction: discord.Interaction, url: str) -> None:
        """Slash command to fetch text content from a URL."""
        await interaction.response.defer()

        try:
            # Fetch and process content
            text = await self._fetch_url_content(url)

            if not text.strip():
                await self.send_interaction_error(
                    interaction,
                    "❌ No Content Found",
                    "No readable text content was found on the provided URL.",
                )
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
            await self.send_interaction_error(
                interaction,
                "❌ Fetch Error",
                f"Failed to fetch content from the URL: {str(e)}",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Error in fetchurl command: %s", e)
            await self.send_interaction_error(
                interaction,
                "❌ Unexpected Error",
                f"An unexpected error occurred: {str(e)}",
            )

    @app_commands.command(name="synccommands", description="Manually sync slash commands")
    @app_commands.checks.has_permissions(administrator=True)
    async def synccommands(self, interaction: discord.Interaction) -> None:
        """Synchronize application commands for this guild."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(f"Synced {len(synced)} command(s).", ephemeral=True)
            self.logger.info(
                "Manually synced %d command(s) in guild: %s",
                len(synced),
                interaction.guild.name if interaction.guild else "N/A",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Failed to sync commands: %s", e)
            await interaction.followup.send(f"Failed to sync commands: {e}", ephemeral=True)

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
                description=f"Successfully synced **{len(synced)}** command(s) for this guild.",
                color=discord.Color.green(),
            )

            await ctx.send(embed=embed)

            self.logger.info(
                "Manually synced %d command(s) in guild: %s via prefix command",
                len(synced),
                ctx.guild.name if ctx.guild else "N/A",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Failed to sync commands via prefix command: %s", e)
            await self.send_error(ctx, "❌ Sync Failed", f"Failed to sync commands: {e}")


async def setup(bot: commands.Bot) -> None:
    """Set up the Admin cog."""
    await bot.add_cog(Admin(bot))
