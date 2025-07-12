"""
Event handlers for GitCord bot.
Handles Discord events like on_ready and command syncing.
"""

import discord
from discord.ext import commands

from .utils.logger import logger
from .config import config


class EventHandler:
    """Handles Discord bot events."""

    def __init__(self, bot: commands.Bot):
        """Initialize the event handler."""
        self.bot = bot

    async def on_ready(self) -> None:
        """Event triggered when the bot is ready and connected to Discord."""
        logger.info('%s has connected to Discord!', self.bot.user)
        logger.info('Bot is in %d guild(s)', len(self.bot.guilds))

        # Set bot status
        await self.bot.change_presence(
            activity=discord.Game(name=config.activity_name)
        )

        # Send restart message to guilds
        await self._send_restart_messages()

        # Sync slash commands
        await self._sync_commands()

    async def _send_restart_messages(self) -> None:
        """Send restart messages to available text channels."""
        for guild in self.bot.guilds:
            logger.info("Connected to guild: %s (ID: %s)", guild.name, guild.id)

            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send("Bot has restarted successfully!")
                        logger.info("Sent restart message to %s in %s", channel.name, guild.name)
                    except Exception as e:
                        logger.error("Failed to send message to %s in %s: %s",
                                   channel.name, guild.name, e)
                    break  # Only send to the first available channel

    async def _sync_commands(self) -> None:
        """Sync slash commands to all guilds and globally."""
        try:
            logger.info("Syncing slash commands...")

            # Sync to all guilds the bot is in
            for guild in self.bot.guilds:
                logger.info("Syncing commands to guild: %s", guild.name)
                synced = await self.bot.tree.sync(guild=guild)
                logger.info("Synced %d command(s) to %s", len(synced), guild.name)

            # Also sync globally (takes up to 1 hour to propagate)
            synced_global = await self.bot.tree.sync()
            logger.info("Synced %d command(s) globally", len(synced_global))

        except Exception as e:
            logger.error("Failed to sync commands: %s", e)


def setup_events(bot: commands.Bot) -> EventHandler:
    """
    Set up event handlers for the bot.

    Args:
        bot: The Discord bot instance

    Returns:
        EventHandler instance
    """
    event_handler = EventHandler(bot)

    # Register event handlers
    bot.add_listener(event_handler.on_ready, 'on_ready')

    return event_handler
