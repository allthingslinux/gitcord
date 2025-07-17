"""
Main GitCord bot class and entry point.
"""

import asyncio

import discord
from discord.ext import commands

from .config import config
from .events import setup_events
from .utils.logger import main_logger as logger


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

        # Command syncing is now done manually using the `/synccommands` slash command.

        logger.info("Bot setup completed")

    async def _load_cogs(self) -> None:
        """Load all bot cogs."""
        # Load the general cog
        await self.load_extension("gitcord.cogs.general")
        logger.info("Loaded general cog")

        # Add more cogs here as they are created
        # await self.load_extension("gitcord.cogs.git")
        # await self.load_extension("gitcord.cogs.admin")

    async def on_command_error(self, context, error):  # pylint: disable=arguments-differ
        """Global command error handler."""
        logger.error("Global command error: %s", error)
        if isinstance(error, commands.CommandNotFound):
            await context.send("Command not found. Try `!hello` or `!ping`!")
        elif isinstance(error, commands.MissingPermissions):
            await context.send("You don't have permission to use this command!")
        elif isinstance(error, commands.CommandError):
            await context.send(f"A command error occurred: {error}")
        else:
            raise error


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
        logger.error("Configuration error: %s", e)


def run_bot() -> None:
    """Entry point to run the bot."""
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
