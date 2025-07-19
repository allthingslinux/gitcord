"""
URL fetching utilities for GitCord bot.
"""

from typing import Union

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from .helpers import create_embed, clean_webpage_text
from .logger import main_logger as logger
from ..constants.messages import ERR_FETCH_ERROR, ERR_UNEXPECTED


async def fetch_url_content(url: str) -> str:
    """
    Fetch and clean content from a URL.

    Args:
        url: The URL to fetch content from

    Returns:
        Cleaned text content from the URL

    Raises:
        requests.exceptions.RequestException: If the request fails
        ValueError: If the content cannot be processed
    """
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


async def handle_fetchurl_command(
    ctx: Union[commands.Context, discord.Interaction], url: str
) -> None:
    """
    Handle the fetchurl command for both prefix and slash commands.

    Args:
        ctx: The command context (can be Context or Interaction)
        url: The URL to fetch content from
    """
    try:
        # Fetch and process content
        text = await fetch_url_content(url)

        if not text.strip():
            embed = create_embed(
                title="❌ No Content Found",
                description="No readable text content was found on the provided URL.",
                color=discord.Color.red(),
            )
            await _send_response(ctx, embed)
            return

        # Create embed with the content
        embed = create_embed(
            title=f"📄 Content from {url}",
            description=f"```\n{text}\n```",
            color=discord.Color.blue(),
            footer=f"Fetched from {url}",
        )

        await _send_response(ctx, embed)

    except requests.exceptions.RequestException as e:
        embed = create_embed(
            title="❌ Fetch Error",
            description=ERR_FETCH_ERROR.format(error=str(e)),
            color=discord.Color.red(),
        )
        await _send_response(ctx, embed)
    except (discord.DiscordException, OSError) as e:
        logger.error("Error in fetchurl command: %s", e)
        embed = create_embed(
            title="❌ Unexpected Error",
            description=ERR_UNEXPECTED.format(error=str(e)),
            color=discord.Color.red(),
        )
        await _send_response(ctx, embed)


async def _send_response(
    ctx: Union[commands.Context, discord.Interaction], embed: discord.Embed
) -> None:
    """
    Send a response based on the context type.

    Args:
        ctx: The command context (Context or Interaction)
        embed: The embed to send
    """
    if isinstance(ctx, commands.Context):
        # Context object (prefix command)
        await ctx.send(embed=embed)
    elif isinstance(ctx, discord.Interaction):
        # Interaction object (slash command)
        await ctx.followup.send(embed=embed)
