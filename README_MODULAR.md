# GitCord - Modular Discord Bot

A modular, pythonic Discord bot for Git integration built with discord.py.

## 🏗️ Architecture

The bot has been restructured into a modular, maintainable architecture:

```
gitcord/
├── __init__.py          # Package initialization
├── bot.py              # Main bot class and entry point
├── config.py           # Configuration management
├── events.py           # Event handlers
├── cogs/               # Discord.py cogs
│   ├── __init__.py
│   └── general.py      # General utility commands
└── utils/              # Utility modules
    ├── __init__.py
    ├── logger.py       # Logging utilities
    └── helpers.py      # Helper functions
```

## 🚀 Features

### Modular Design
- **Separation of Concerns**: Each module has a specific responsibility
- **Cog-based Commands**: Commands are organized into cogs for better maintainability
- **Configuration Management**: Centralized configuration with environment variables
- **Event Handling**: Dedicated event handler class
- **Utility Functions**: Reusable helper functions and logging

### Pythonic Code
- **Type Hints**: Full type annotation support
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Proper exception handling with logging
- **Async/Await**: Modern async programming patterns
- **Properties**: Clean property-based configuration access

### Enhanced Features
- **Rich Embeds**: Beautiful Discord embeds for responses
- **Structured Logging**: Proper logging with formatting
- **Command Syncing**: Use the `/synccommands` slash command to synchronize application commands
- **Error Recovery**: Graceful error handling and recovery

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gitcord
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   python setup_env.py
   ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

## 🔧 Configuration

The bot uses a centralized configuration system in `gitcord/config.py`:

```python
from gitcord.config import config

# Access configuration
token = config.token
prefix = config.prefix
activity_name = config.activity_name
```

### Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token (required)

## 📝 Usage

### Running the Bot
```bash
# Direct execution
python main.py

# Using the console script (after installation)
gitcord

# Development mode
python -m gitcord.bot
```

### Adding New Commands
1. **Create a new cog** in `gitcord/cogs/`:
   ```python
   import discord
   from discord.ext import commands
   
   class MyCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
       
       @commands.command()
       async def mycommand(self, ctx):
           await ctx.send("Hello!")
   
   async def setup(bot):
       await bot.add_cog(MyCog(bot))
   ```

2. **Register the cog** in `gitcord/bot.py`:
   ```python
   await self.load_extension("gitcord.cogs.my_cog")
   ```

### Adding New Events
1. **Extend the EventHandler** in `gitcord/events.py`:
   ```python
   async def on_message(self, message):
       # Handle message events
       pass
   ```

2. **Register the event** in `setup_events()`:
   ```python
   bot.add_listener(event_handler.on_message, 'on_message')
   ```

## 🛠️ Development

### Project Structure
- **`gitcord/bot.py`**: Main bot class and entry point
- **`gitcord/config.py`**: Configuration management
- **`gitcord/events.py`**: Event handlers
- **`gitcord/cogs/`**: Command cogs
- **`gitcord/utils/`**: Utility functions

### Adding Utilities
1. **Create utility functions** in `gitcord/utils/`:
   ```python
   def my_utility_function():
       return "Hello from utility!"
   ```

2. **Import and use** in your cogs:
   ```python
   from ..utils.helpers import my_utility_function
   ```

### Logging
The bot uses structured logging:

```python
from gitcord.utils.logger import logger

logger.info("Information message")
logger.error("Error message")
logger.debug("Debug message")
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Quality
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black gitcord/

# Lint code
flake8 gitcord/

# Type checking
mypy gitcord/
```

## 📚 API Reference

### Configuration
- `config.token`: Discord bot token
- `config.prefix`: Command prefix
- `config.activity_name`: Bot activity name

### Utilities
- `format_latency(latency)`: Format latency in milliseconds
- `create_embed(title, description, ...)`: Create Discord embed
- `truncate_text(text, max_length)`: Truncate text to max length
- `format_time_delta(seconds)`: Format time delta

### Logging
- `logger.info(message)`: Log information
- `logger.error(message)`: Log error
- `logger.debug(message)`: Log debug message

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [documentation](README.md)
2. Search existing [issues](../../issues)
3. Create a new issue with detailed information

---

**Happy coding! 🎉** 