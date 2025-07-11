"""
General commands cog for GitCord bot.
Contains basic utility commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import requests
from bs4 import BeautifulSoup
import re

from ..utils.logger import logger
from ..utils.helpers import format_latency, create_embed


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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            
        except Exception as e:
            logger.error(f"Error in fetchurl command: {e}")
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            
        except Exception as e:
            logger.error(f"Error in fetchurl command: {e}")
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