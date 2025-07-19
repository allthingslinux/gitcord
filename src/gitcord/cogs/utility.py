"""
Basic utility commands cog for GitCord bot.
Contains simple utility commands like greetings and latency checks.
"""

import discord
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import create_embed, format_latency
from ..utils.logger import main_logger as logger


class Utility(commands.Cog):
    """Basic utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Utility cog."""
        self.bot = bot
        logger.info("Utility cog loaded")

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context) -> None:
        """Simple hello world command."""
        embed = create_embed(
            title="👋 Welcome!",
            description=f"Hello, {ctx.author.mention}! Welcome to GitCord!",
            color=discord.Color.blue(),
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


async def setup(bot: commands.Bot) -> None:
    """Set up the Utility cog."""
    await bot.add_cog(Utility(bot))
