# GitCord Bot Setup Guide

This guide will help you set up the GitCord Discord bot on your server.

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **A Discord bot token** (see [Creating a Discord Bot](#creating-a-discord-bot) below)

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

You have two options:

#### Option A: Use the Setup Script (Recommended)
```bash
python setup.py
```
This will guide you through creating the `.env` file with your bot token.

#### Option B: Manual Setup
Create a `.env` file in the project root with:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Run the Bot

```bash
python bot.py
```

If everything is set up correctly, you should see:
```
Starting GitCord bot...
[Bot Name] has connected to Discord!
Bot is in X guild(s)
```

## Creating a Discord Bot

If you don't have a Discord bot yet, follow these steps:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under the "Token" section, click "Copy" to copy your bot token
6. Save this token securely - you'll need it for the `.env` file

### Bot Permissions

Make sure your bot has these permissions:
- Send Messages
- Read Message History
- Use Slash Commands (if you plan to use them later)

## Bot Commands

Once the bot is running, you can use these commands in your Discord server:

- `!hello` - Get a friendly greeting from the bot
- `!ping` - Check the bot's latency

## Troubleshooting

### "DISCORD_TOKEN not found in environment variables"
- Make sure you have a `.env` file in the project root
- Check that the file contains `DISCORD_TOKEN=your_token_here`
- Ensure there are no extra spaces or quotes around the token

### "Invalid Discord token"
- Double-check your bot token from the Discord Developer Portal
- Make sure you copied the entire token correctly
- Verify the bot is still active in the Developer Portal

### Bot not responding to commands
- Ensure the bot has been invited to your server with proper permissions
- Check that the bot is online (green status)
- Verify you're using the correct command prefix (`!`)

## Next Steps

This is a basic hello world bot. For the full GitCord functionality (GitHub integration, server configuration management), check the main [README.md](README.md) for development status and roadmap.

## Security Notes

- Never share your bot token publicly
- The `.env` file is already in `.gitignore` to prevent accidental commits
- If your token is ever compromised, regenerate it in the Discord Developer Portal 