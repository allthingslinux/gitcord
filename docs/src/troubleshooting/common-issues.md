# Common Issues

Fix common GitCord problems.

## Bot Connection Issues

### Bot Not Responding

**Problem:** Bot is online but doesn't respond to commands.

**Fix:**
1. Check bot permissions in server settings
2. Try `!ping` to test basic functionality
3. Run `/synccommands` to update slash commands
4. Check your bot token is correct

### Bot Won't Start

**Problem:** Bot fails to start with login errors.

**Fix:**
1. Check your bot token in `.env` file
2. Make sure no extra spaces in token
3. Regenerate token if needed
4. Check your internet connection

## Channel Issues

### Channel Creation Fails

**Problem:** `!createchannel` or `/createcategory` commands fail.

**Fix:**
1. Check YAML file exists and path is correct
2. Validate YAML syntax (use a validator)
3. Make sure you have "Manage Channels" permission
4. Check all required fields are present

### Channel Type Errors

**Problem:** "Channel type 'xyz' is not supported"

**Fix:**
- Use only "text", "voice", or "category"
- Check spelling in your YAML file

## Permission Issues

### Permission Denied

**Problem:** "You don't have permission to use this command!"

**Fix:**
- Check your role permissions in server
- Make sure you have the right permission level
- Contact a server administrator

### Bot Permission Issues

**Problem:** Bot can't perform actions

**Fix:**
- Check bot's role permissions in server settings
- Make sure bot's role is above roles it manages
- Give bot "Manage Channels" permission

## YAML Issues

### Invalid YAML

**Problem:** "Failed to parse YAML file"

**Fix:**
- Use a YAML validator to check syntax
- Check indentation (use spaces, not tabs)
- Make sure all quotes match
- Verify all required fields are present

### Missing Fields

**Problem:** "Missing required field"

**Fix:**
- Check your YAML has all required fields
- Required: `name`, `type`, `position`
- Optional: `topic`, `nsfw`, `user_limit`

## Network Issues

### URL Fetching Fails

**Problem:** `!fetchurl` command fails

**Fix:**
- Check the URL is valid and accessible
- Make sure URL starts with http:// or https://
- Try a different URL to test
- Check your internet connection

## Performance Issues

### Bot is Slow

**Problem:** Commands take a long time to respond

**Fix:**
- Check your internet connection
- Restart the bot
- Check Discord's status
- Reduce complexity of YAML files

## Getting Help

If you still have problems:

1. Check the [Error Messages](./error-messages.md) page
2. Enable [Debug Mode](./debug-mode.md) for more info
3. Check the bot logs for error details
4. Ask for help in the project's GitHub issues
