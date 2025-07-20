# Configuration

Learn how to configure GitCord to suit your needs.

## Environment Variables

GitCord uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Required: Your Discord bot token
DISCORD_TOKEN=your_bot_token_here

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Optional: Bot prefix for legacy commands (default: !)
COMMAND_PREFIX=!

# Optional: Database URL for persistent storage
DATABASE_URL=sqlite:///gitcord.db
```

## Bot Configuration

### Permissions

Ensure your bot has these permissions:

- **Manage Channels**: Create, edit, and delete channels
- **Manage Roles**: Set up channel permissions
- **Send Messages**: Send responses to commands
- **Embed Links**: Send rich embeds
- **Use Slash Commands**: Register and use slash commands
- **Attach Files**: Upload template files

### Intents

The bot requires these Discord intents:

- **Guilds**: Access server information
- **Guild Messages**: Read and send messages
- **Message Content**: Read message content for prefix commands

## Template Configuration

### YAML Structure

Templates use YAML format with this structure:

```yaml
# Single channel
name: channel-name
type: text|voice|category
topic: Optional channel topic
position: Optional position number
nsfw: Optional boolean for NSFW channels

# Category with channels
name: category-name
type: category
channels:
  - name: channel-1
    type: text
    topic: Channel description
  - name: channel-2
    type: voice
    topic: Voice channel description
```

### Template Locations

Templates can be stored in:

1. **Built-in templates**: `gitcord-template/` directory
2. **Custom templates**: Upload via Discord commands
3. **Local files**: Reference local YAML files

## Logging Configuration

Configure logging in your environment:

```env
# Log level options
LOG_LEVEL=DEBUG    # Most verbose
LOG_LEVEL=INFO     # Standard information
LOG_LEVEL=WARNING  # Warnings and errors only
LOG_LEVEL=ERROR    # Errors only
```

## Database Configuration

For persistent storage, configure a database:

```env
# SQLite (default)
DATABASE_URL=sqlite:///gitcord.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/gitcord

# MySQL
DATABASE_URL=mysql://user:password@localhost/gitcord
```

## Custom CSS and JavaScript

Add custom styling to the documentation:

1. Create `docs/src/custom.css`:
   ```css
   /* Custom styles */
   .book-summary {
       background-color: #f5f5f5;
   }
   ```

2. Create `docs/src/custom.js`:
   ```javascript
   // Custom JavaScript
   console.log('GitCord documentation loaded');
   ```

## Advanced Configuration

### Command Cooldowns

Configure command cooldowns in the bot code:

```python
# In cog files
@commands.cooldown(1, 30, commands.BucketType.guild)
async def create_channel(self, ctx):
    # Command implementation
```

### Error Handling

Customize error handling:

```python
# Global error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
```

## Security Considerations

- Keep your bot token secure and never commit it to version control
- Use environment variables for sensitive configuration
- Regularly rotate your bot token
- Limit bot permissions to only what's necessary
- Monitor bot activity and logs

## Troubleshooting Configuration

### Common Issues

1. **Bot not responding**: Check token and permissions
2. **Commands not working**: Verify slash commands are registered
3. **Template errors**: Validate YAML syntax
4. **Permission errors**: Ensure bot has required permissions

### Debug Mode

Enable debug mode for detailed logging:

```env
LOG_LEVEL=DEBUG
```

This provides verbose output for troubleshooting configuration issues.

## Next Steps

- Learn about [Available Commands](../user-guide/commands.md)
- Explore [Template Creation](../templates/custom-templates.md)
- Check [Troubleshooting](../troubleshooting/common-issues.md) for help 