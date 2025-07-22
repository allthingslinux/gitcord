"""
Help system cog for GitCord bot.
Contains help commands and documentation links.
"""

import discord
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import create_embed
from ..utils.logger import main_logger as logger


class Help(commands.Cog):
    """Help system commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Help cog."""
        self.bot = bot
        logger.info("Help cog loaded")

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context) -> None:
        """Prefix command to show help information and link to the wiki."""
        embed = create_embed(
            title="🤖 GitCord Help",
            description="Welcome to GitCord! Here's how to get help and learn more about the bot."
        )

        embed.add_field(
            name="📚 Documentation",
            value=(
                "For detailed documentation, tutorials, and guides, visit our "
                "[Wiki](https://github.com/evolvewithevan/gitcord/wiki)\n"
                "To see current issues, visit our "
                "[GitHub Issues](https://github.com/users/evolvewithevan/projects/4/views/1)"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔧 Available Commands",
            value="• `!hello` - Get a friendly greeting\n"
            "• `!help` - Show help information and link to the wiki (***YOU ARE HERE***)\n"
            "• `!ping` - Check bot latency\n"
            "• `!createchannel` - Create a channel from YAML (Requires Manage Channels)\n"
            "• `!createcategory` - Create a category from YAML (Requires Manage Channels)\n"
            "• `!git clone <url> [-b branch]` - Clone a template repo for this server (Admin only)\n"
            "• `!git pull` - Pull latest changes and apply template (Admin only)\n"
            "• `!synccommands` - Sync slash commands (Admin only)\n"
            "• `!applytemplate` - (Deprecated) Use !git clone and !git pull instead",
            inline=False,
        )

        embed.add_field(
            name="⚡ Slash Commands",
            value="• `/slashping` - Check bot latency\n"
            "• `/createcategory [yaml_path]` - Create category from YAML (Requires Manage Channels)\n"
            "• `/synccommands` - Sync slash commands (Admin only)\n"
            "• `/applytemplate` - (Deprecated) Use !git clone and !git pull instead",
            inline=False,
        )

        embed.add_field(
            name="🔗 Quick Links",
            value="• [GitHub Repository](https://github.com/evolvewithevan/gitcord)\n"
            "• [Github Project](https://github.com/users/evolvewithevan/projects/4/views/1)\n"
            "• [Roadmap](https://github.com/users/evolvewithevan/projects/4/views/3)\n"
            "• [Wiki Documentation](https://github.com/evolvewithevan/gitcord/wiki)\n"
            "• [Security Policy](https://github.com/evolvewithevan/gitcord/blob/main/SECURITY.md)",
            inline=False,
        )

        embed.set_footer(text="GitCord - Discord bot for GitOps-based server structure. For more, see the Wiki.")

        await ctx.send(embed=embed)

    @app_commands.command(
        name="help", description="Show help information and link to the wiki"
    )
    async def help_slash(self, interaction: discord.Interaction) -> None:
        """Slash command to show help information and link to the wiki."""
        embed = create_embed(
            title="🤖 GitCord Help",
            description="Welcome to GitCord! Here's how to get help and learn more about the bot."
        )

        embed.add_field(
            name="📚 Documentation",
            value=(
                "For detailed documentation, tutorials, and guides, visit our "
                "[Wiki](https://github.com/evolvewithevan/gitcord/wiki)\n"
                "To see current issues, visit our "
                "[GitHub Issues](https://github.com/users/evolvewithevan/projects/4/views/1)"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔧 Available Commands",
            value="• `!hello` - Get a friendly greeting\n"
            "• `!help` - Show help information and link to the wiki (***YOU ARE HERE***)\n"
            "• `!ping` - Check bot latency\n"
            "• `!createchannel` - Create a channel from YAML (Requires Manage Channels)\n"
            "• `!createcategory` - Create a category from YAML (Requires Manage Channels)\n"
            "• `!git clone <url> [-b branch]` - Clone a template repo for this server (Admin only)\n"
            "• `!git pull` - Pull latest changes and apply template (Admin only)\n"
            "• `!synccommands` - Sync slash commands (Admin only)\n"
            "• `!applytemplate` - (Deprecated) Use !git clone and !git pull instead",
            inline=False,
        )

        embed.add_field(
            name="⚡ Slash Commands",
            value="• `/slashping` - Check bot latency\n"
            "• `/createcategory [yaml_path]` - Create category from YAML (Requires Manage Channels)\n"
            "• `/synccommands` - Sync slash commands (Admin only)\n"
            "• `/applytemplate` - (Deprecated) Use !git clone and !git pull instead",
            inline=False,
        )

        embed.add_field(
            name="🔗 Quick Links",
            value="• [GitHub Repository](https://github.com/evolvewithevan/gitcord)\n"
            "• [Github Project](https://github.com/users/evolvewithevan/projects/4/views/1)\n"
            "• [Roadmap](https://github.com/users/evolvewithevan/projects/4/views/3)\n"
            "• [Wiki Documentation](https://github.com/evolvewithevan/gitcord/wiki)\n"
            "• [Security Policy](https://github.com/evolvewithevan/gitcord/blob/main/SECURITY.md)",
            inline=False,
        )

        embed.set_footer(text="GitCord - Discord bot for GitOps-based server structure. For more, see the Wiki.")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Set up the Help cog."""
    await bot.add_cog(Help(bot))
