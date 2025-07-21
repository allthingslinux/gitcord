# Configuration

Set up GitCord for your needs.

## Environment Variables

Create a `.env` file in the project root:

```env
# Required: Your Discord bot token
DISCORD_TOKEN=your_bot_token_here

# Optional: Bot prefix for commands (default: !)
PREFIX=!
```

## Bot Permissions

Your bot needs these permissions:

- **Manage Channels**: Create, edit, and delete channels
- **Send Messages**: Send responses to commands
- **Embed Links**: Send rich embeds
- **Use Slash Commands**: Register and use slash commands

## Discord Intents

The bot needs these Discord intents:

- **Guilds**: Access server information
- **Guild Messages**: Read and send messages
- **Message Content**: Read message content for prefix commands

## YAML Templates

Templates use YAML format:

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
  - channel-1
  - channel-2
```

## Template Locations

Templates are available exclusively at:

- [gitcord-template GitHub Repository](https://github.com/evolvewithevan/gitcord-template)

## Logging

GitCord uses Python's built-in logging. Logs go to the console by default.

**Note:** Database configuration and advanced options are not currently available.

## Security

- Keep your bot token secure
- Never commit tokens to version control
- Use environment variables for sensitive data
- Regularly rotate your bot token
- Give bot only necessary permissions

## Problems?

### Common Issues

1. **Bot not responding**: Check token and permissions
2. **Commands not working**: Verify slash commands are registered
3. **Template errors**: Check YAML syntax
4. **Permission errors**: Ensure bot has required permissions

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG=true
```

## Next Steps

- Learn about [Available Commands](../user-guide/commands.md)
- Explore [Template Creation](../templates/custom-templates.md)
- Check [Troubleshooting](../troubleshooting/common-issues.md) for help 