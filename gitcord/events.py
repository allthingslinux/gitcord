"""
Event handlers for GitCord bot.
Handles Discord events like on_ready and command syncing.
"""

import discord
from discord.ext import commands
from typing import List

from .utils.logger import logger
from .config import config


class EventHandler:
    """Handles Discord bot events."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the event handler."""
        self.bot = bot
    
    async def on_ready(self) -> None:
        """Event triggered when the bot is ready and connected to Discord."""
        logger.info(f'{self.bot.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.bot.guilds)} guild(s)')
        
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
            logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
            
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send("Bot has restarted successfully!")
                        logger.info(f"Sent restart message to {channel.name} in {guild.name}")
                    except Exception as e:
                        logger.error(f"Failed to send message to {channel.name} in {guild.name}: {e}")
                    break  # Only send to the first available channel
    
    async def _sync_commands(self) -> None:
        """Sync slash commands to all guilds and globally."""
        try:
            logger.info("Syncing slash commands...")
            
            # Sync to all guilds the bot is in
            for guild in self.bot.guilds:
                logger.info(f"Syncing commands to guild: {guild.name}")
                synced = await self.bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} command(s) to {guild.name}")
            
            # Also sync globally (takes up to 1 hour to propagate)
            synced_global = await self.bot.tree.sync()
            logger.info(f"Synced {len(synced_global)} command(s) globally")
            
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")


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