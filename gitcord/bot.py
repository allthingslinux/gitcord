"""
Main GitCord bot class and entry point.
"""

import discord
from discord.ext import commands
import asyncio

from .config import config
from .events import setup_events
from .utils.logger import logger


class GitCordBot(commands.Bot):
    """Main GitCord bot class."""
    
    def __init__(self):
        """Initialize the GitCord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None  # We can implement a custom help command later
        )
        
        # Set up event handlers
        self.event_handler = setup_events(self)
        
        logger.info("GitCord bot initialized")
    
    async def setup_hook(self) -> None:
        """Setup hook to register slash commands and load cogs."""
        logger.info("Setting up bot...")
        
        # Load cogs
        await self._load_cogs()
        
        # Sync command tree
        await self.tree.sync()
        
        logger.info("Bot setup completed")
    
    async def _load_cogs(self) -> None:
        """Load all bot cogs."""
        try:
            # Load the general cog
            await self.load_extension("gitcord.cogs.general")
            logger.info("Loaded general cog")
            
            # Add more cogs here as they are created
            # await self.load_extension("gitcord.cogs.git")
            # await self.load_extension("gitcord.cogs.admin")
            
        except Exception as e:
            logger.error(f"Failed to load cogs: {e}")
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global command error handler."""
        logger.error(f"Global command error: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Try `!hello` or `!ping`!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        else:
            await ctx.send(f"An error occurred: {error}")


async def main() -> None:
    """Main function to run the bot."""
    try:
        # Create and run the bot
        bot = GitCordBot()
        logger.info("Starting GitCord bot...")
        await bot.start(config.token)
        
    except discord.LoginFailure:
        logger.error("Invalid Discord token! Please check your DISCORD_TOKEN in the .env file.")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")


def run_bot() -> None:
    """Entry point to run the bot."""
    asyncio.run(main())


if __name__ == "__main__":
    run_bot() 