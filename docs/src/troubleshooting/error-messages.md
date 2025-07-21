# Error Messages

Common GitCord error messages and how to fix them.

## Authentication Errors

### Invalid Discord Token

**Error:**
```
Invalid Discord token! Please check your DISCORD_TOKEN in the .env file.
```

**Fix:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to "Bot" section
4. Click "Reset Token" to get a new token
5. Update your `.env` file

### Login Failure

**Error:**
```
discord.errors.LoginFailure: 401 Unauthorized
```

**Fix:**
- Check your bot token is correct
- Make sure bot application exists and is active

## Permission Errors

### Missing Permissions

**Error:**
```
You don't have permission to use this command!
```

**Fix:**
- Check your role permissions in server
- Make sure you have the right permission level
- Contact a server administrator

### Bot Permission Issues

**Error:**
```
discord.errors.Forbidden: 403 Forbidden (error code: 50013): Missing Permissions
```

**Fix:**
- Go to Server Settings → Roles
- Make sure bot's role has necessary permissions
- Move bot's role higher in the role list

## Command Errors

### Command Not Found

**Error:**
```
Command not found. Try `!help` for available commands.
```

**Fix:**
- Check command spelling
- Run `/synccommands` to update slash commands
- Try `!help` to see available commands

## YAML Errors

### File Not Found

**Error:**
```
YAML file not found at: {path}
```

**Fix:**
- Check the file path is correct
- Make sure the file exists
- Use the right path format

### Invalid YAML

**Error:**
```
Failed to parse YAML file: {error}
```

**Fix:**
- Use a YAML validator to check syntax
- Check indentation (use spaces, not tabs)
- Make sure all quotes match

### Missing Required Field

**Error:**
```
Missing required field: {field}
```

**Fix:**
- Add the missing field to your YAML
- Required fields: `name`, `type`, `position`
- Check field spelling

### Invalid Channel Type

**Error:**
```
Channel type '{type}' is not supported. Use 'text' or 'voice'.
```

**Fix:**
- Use only "text", "voice", or "category"
- Check spelling in your YAML file

## Network Errors

### Fetch Error

**Error:**
```
Failed to fetch content from the URL: {error}
```

**Fix:**
- Check the URL is valid and accessible
- Make sure URL starts with http:// or https://
- Try a different URL to test

### No Content Found

**Error:**
```
No readable text content was found on the provided URL.
```

**Fix:**
- Try a different website
- Check if the website has text content
- Some websites block content fetching

## Discord API Errors

### Discord API Error

**Error:**
```
Discord API error: {error}
```

**Fix:**
- Check Discord's status
- Wait a few minutes and try again
- Check your internet connection

### Unexpected Error

**Error:**
```
An unexpected error occurred: {error}
```

**Fix:**
- Restart the bot
- Check the bot logs for more details
- Report the issue with error details

## Getting Help

If you can't fix the error:

1. Copy the exact error message
2. Check the [Common Issues](./common-issues.md) page
3. Enable [Debug Mode](./debug-mode.md) for more info
4. Ask for help in the project's GitHub issues
