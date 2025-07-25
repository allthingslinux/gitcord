"""
Message constants for GitCord bot.
"""

# Error messages
ERR_PERMISSION_DENIED = "You do not have the required permission to use this command."
ERR_FILE_NOT_FOUND = "YAML file not found at: {path}"
ERR_INVALID_YAML = "Failed to parse YAML file: {error}"
ERR_INVALID_CONFIG = "Missing required field: {field}"
ERR_INVALID_CHANNEL_TYPE = (
    "Channel type '{type}' is not supported. Use 'text' or 'voice'."
)
ERR_DISCORD_API = "Discord API error: {error}"
ERR_UNEXPECTED = "An unexpected error occurred: {error}"
ERR_RATE_LIMITED = (
    "You're sending commands too quickly! "
    "Please wait **{time_left}s** before trying again.\n\n"
    "**Rate Limit:** {max_commands} command(s) per {window} seconds"
)

# Success messages
SUCCESS_CATEGORY_CREATED = "Successfully created category: **{name}**"
SUCCESS_CHANNEL_CREATED = "Successfully created channel: {mention}"
SUCCESS_CATEGORY_UPDATED = "Successfully processed category: **{name}**"
SUCCESS_COMMANDS_SYNCED = "Successfully synced **{count}** command(s) to this guild."

# Help text content (for help command)
HELP_DOCS = (
    "For detailed documentation, tutorials, and guides, visit our "
    "[Wiki](https://github.com/evolvewithevan/gitcord/wiki)\n"
    "To see current issues, visit our "
    "[GitHub Issues](https://github.com/users/evolvewithevan/projects/4/views/1)"
)
HELP_COMMANDS = (
    "• `!hello` - Get a friendly greeting\n"
    "• `!help` - Show help information and link to the wiki (***YOU ARE HERE***)\n"
    "• `!ping` - Check bot latency\n"
    "• `!createchannel` - Create a channel from YAML (Manage Channels)\n"
    "• `!createcategory` - Create a category from YAML (Manage Channels)\n"
    "• `!synccommands` - Sync slash commands (Admin only)"
)