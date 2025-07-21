# Installation

Set up GitCord on your Discord server.

## What You Need

- Python 3.8 or higher
- A Discord bot token
- Discord server with admin permissions

## Step 1: Get the Code

```bash
git clone https://github.com/evolvewithevan/gitcord.git
cd gitcord
```

## Step 2: Install Dependencies

### Using pip (Not Recommended)

```bash
pip install -r requirements.txt
```

### Using uv (Recommended)

```bash
uv sync
```

## Step 3: Set Up Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Populate the `.env` file with your bot token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

## Step 4: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token and add it to your `.env` file
5. Enable the following bot permissions:
   - Manage Channels
   - Manage Roles (Technically not needed until Role Management is implemented)
   - Send Messages
   - Embed Links
   - Use Slash Commands

## Step 5: Invite Bot to Server

Use this URL (replace `YOUR_CLIENT_ID` with your bot's client ID):

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

## Step 6: Run the Bot

```bash
python -m gitcord
```

## Verification

Once the bot is running, you should see:
- A startup message in the console
- The bot appears online in your Discord server
- Slash commands are available

## Next Steps

- Check out the [Quick Start Guide](./quick-start.md) to create your first channels
- Learn about [Configuration](./configuration.md) options
- Explore available [Commands](../user-guide/commands.md)

## Troubleshooting

If you encounter issues during installation:

- Ensure Python 3.8+ is installed: `python --version`
- Verify all dependencies are installed: `pip list`
- Check your bot token is correct
- Ensure the bot has proper permissions in your server

For more help, see the [Troubleshooting](../troubleshooting/common-issues.md) section. 