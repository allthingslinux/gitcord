"""
Base cog class with common functionality.
"""

import logging

import discord
from discord.ext import commands

from ..utils.helpers import (
    create_error_embed,
    create_success_embed,
    handle_command_error,
    handle_interaction_error,
)


class BaseCog(commands.Cog):
    """Base cog class with common functionality."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(f"gitcord.{self.__class__.__name__.lower()}")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle errors for all commands in this cog."""
        await handle_command_error(ctx, error, self.logger)

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ) -> None:
        """Handle errors for all app commands in this cog."""
        await handle_interaction_error(interaction, error, self.logger)

    def create_error_embed(self, title: str, description: str) -> discord.Embed:
        """Create a standardized error embed."""
        return create_error_embed(title, description)

    def create_success_embed(self, title: str, description: str) -> discord.Embed:
        """Create a standardized success embed."""
        return create_success_embed(title, description)

    async def send_error(
        self, ctx: commands.Context, title: str, description: str
    ) -> None:
        """Send an error embed."""
        embed = self.create_error_embed(title, description)
        await ctx.send(embed=embed)

    async def send_success(
        self, ctx: commands.Context, title: str, description: str
    ) -> None:
        """Send a success embed."""
        embed = self.create_success_embed(title, description)
        await ctx.send(embed=embed)

    async def send_interaction_error(
        self, interaction: discord.Interaction, title: str, description: str
    ) -> None:
        """Send an error embed via interaction."""
        embed = self.create_error_embed(title, description)
        await interaction.followup.send(embed=embed)

    async def send_interaction_success(
        self, interaction: discord.Interaction, title: str, description: str
    ) -> None:
        """Send a success embed via interaction."""
        embed = self.create_success_embed(title, description)
        await interaction.followup.send(embed=embed)
