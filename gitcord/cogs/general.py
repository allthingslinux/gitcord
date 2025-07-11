"""
General commands cog for GitCord bot.
Contains basic utility commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from ..utils.logger import logger
from ..utils.helpers import format_latency, create_embed


class General(commands.Cog):
    """General utility commands."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the General cog."""
        self.bot = bot
        logger.info("General cog loaded")
    
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
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Try `!hello` or `!ping`!")
        else:
            logger.error(f"Command error in {ctx.command}: {error}")
            await ctx.send(f"An error occurred: {error}")


async def setup(bot: commands.Bot) -> None:
    """Set up the General cog."""
    await bot.add_cog(General(bot)) 