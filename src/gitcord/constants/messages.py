"""
Message constants for GitCord bot.
"""

# Error messages
ERR_PERMISSION_DENIED = "You do not have the required permission to use this command."
ERR_FILE_NOT_FOUND = "YAML file not found at: {path}"
ERR_INVALID_YAML = "Failed to parse YAML file: {error}"
ERR_INVALID_CONFIG = "Missing required field: {field}"
ERR_INVALID_CHANNEL_TYPE = "Channel type '{type}' is not supported. Use 'text' or 'voice'."
ERR_DISCORD_API = "Discord API error: {error}"
ERR_UNEXPECTED = "An unexpected error occurred: {error}"
ERR_NO_CONTENT_FOUND = "No readable text content was found on the provided URL."
ERR_FETCH_ERROR = "Failed to fetch content from the URL: {error}"

# Success messages
SUCCESS_CATEGORY_CREATED = "Successfully created category: **{name}**"
SUCCESS_CHANNEL_CREATED = "Successfully created channel: {mention}"
SUCCESS_CATEGORY_UPDATED = "Successfully processed category: **{name}**"
SUCCESS_COMMANDS_SYNCED = "Successfully synced **{count}** command(s) to this guild."

# Help text content (for help command)
HELP_DOCS = "For detailed documentation, tutorials, and guides, visit our [Wiki](https://github.com/evolvewithevan/gitcord/wiki)\nTo see current issues, visit our [GitHub Issues](https://github.com/users/evolvewithevan/projects/4/views/1)"
HELP_COMMANDS = "• `!hello` - Get a friendly greeting\n• `!help` - Show help information and link to the wiki (***YOU ARE HERE***)\n• `!ping` - Check bot latency\n• `!fetchurl <url>` - Fetch content from a URL (Admin only)\n• `!createchannel` - Create a channel from YAML (Manage Channels)\n• `!createcategory` - Create a category from YAML (Manage Channels)\n• `!synccommands` - Sync slash commands (Admin only)"
HELP_SLASH_COMMANDS = "• `/slashping` - Check bot latency\n• `/fetchurl <url>` - Fetch content from a URL (Admin only)\n• `/createcategory [yaml_path]` - Create category from YAML (Manage Channels)\n• `/synccommands` - Sync slash commands (Admin only)"
HELP_LINKS = "• [GitHub Repository](https://github.com/evolvewithevan/gitcord)\n• [Github Project](https://github.com/users/evolvewithevan/projects/4/views/1)\n• [Roadmap](https://github.com/users/evolvewithevan/projects/4/views/3)\n• [Wiki Documentation](https://github.com/evolvewithevan/gitcord/wiki)\n• [Security Policy](https://github.com/evolvewithevan/gitcord/blob/main/SECURITY.md)"
HELP_FOOTER = "GitCord - Discord bot for GitOps based server structure management"

# UI button labels
DELETE_EXTRA_CHANNELS_LABEL = "Delete Extra Channel(s)" 