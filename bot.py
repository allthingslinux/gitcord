import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!hello"))

    # Send "Bot has restarted successfully!" to the first available text channel in each guild
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} (ID: {guild.id})")
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send("Bot has restarted successfully!")
                except Exception as e:
                    print(f"Failed to send message to {channel.name} in {guild.name}: {e}")
                break  # Only send to the first available channel

    # Sync slash commands
    try:
        print("Syncing slash commands...")
        # Sync to all guilds the bot is in
        for guild in bot.guilds:
            print(f"Syncing commands to guild: {guild.name}")
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to {guild.name}")
        
        # Also sync globally (takes up to 1 hour to propagate)
        synced_global = await bot.tree.sync()
        print(f"Synced {len(synced_global)} command(s) globally")
        
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Slash command to check bot latency."""
    await interaction.response.send_message("Pong!")

@bot.command(name='hello')
async def hello(ctx):
    """Simple hello world command."""
    await ctx.send(f'Hello, {ctx.author.mention}! 👋 Welcome to GitCord!')

@bot.command(name='ping')
async def ping_prefix(ctx):
    """Check bot latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! 🏓 Latency: {latency}ms')

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Try `!hello` or `!ping`!")
    else:
        await ctx.send(f"An error occurred: {error}")

def main():
    """Main function to run the bot."""
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please set your Discord bot token in the .env file.")
        return
    
    try:
        print("Starting GitCord bot...")
        bot.run(token)
    except discord.LoginFailure:
        print("Error: Invalid Discord token!")
        print("Please check your DISCORD_TOKEN in the .env file.")
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    main() 