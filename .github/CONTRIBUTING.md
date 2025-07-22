# Contributing to GitCord

Thank you for your interest in contributing to GitCord! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Overview](#project-overview)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Release Process](#release-process)

## Code of Conduct

This project is governed by the GNU General Public License v3.0. By participating, you are expected to uphold this license and contribute to a respectful, inclusive community.

## Project Overview

GitCord is a Discord bot that integrates with GitHub to manage Discord server configurations through version-controlled configuration files. The project is currently in early development (Alpha stage) and uses:

- **Python 3.9+** with Discord.py
- **YAML** for configuration files
- **GitOps** approach for server management
- **GPL-3.0** license

### Current Status

⚠️ **Important**: This project is currently in early development. The bot exists as a basic framework with limited functionality

**Do not run this on servers with untrusted members present. It is not secure yet.**

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A Discord bot token (for testing)
- GitHub account (for contributing)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/evolvewithevan/gitcord.git
   cd gitcord
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or using uv (recommended)
   uv sync
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # If .env.example exists
   # Edit .env with your Discord bot token and other settings
   ```

5. **Run the bot**
   ```bash
   python -m gitcord
   # Or using the installed script
   gitcord
   ```

### Project Structure

```
gitcord/
├── src/gitcord/           # Main source code
│   ├── bot.py            # Main bot entry point
│   ├── config.py         # Configuration management
│   ├── events.py         # Discord event handlers
│   ├── cogs/             # Discord.py cogs (command modules)
│   ├── utils/            # Utility functions
│   ├── views/            # Discord UI components
│   └── constants/        # Constants and messages
├── gitcord-template/     # Template repository structure
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata and build config
└── README.md            # Project documentation
```

## Contribution Workflow

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/evolvewithevan/gitcord.git
   ```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

- Follow the [coding standards](#coding-standards)
- Write tests for new functionality
- Update documentation as needed
- Keep commits atomic and well-described

### 4. Test Your Changes

```bash
# Run linting
pylint src/gitcord/

# Run tests (when available)
python -m pytest

# Test the bot locally
python -m gitcord
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with a clear description of your changes.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Maximum line length: 88 characters (Black formatter default)
- Use meaningful variable and function names

### Discord.py Best Practices

- Use Discord.py 2.5.2+ features
- Implement proper error handling for Discord API calls
- Use slash commands where possible
- Follow Discord's rate limiting guidelines

### Code Organization

- Keep cogs focused on specific functionality
- Use utility functions for reusable code
- Maintain separation of concerns
- Document complex functions and classes

### Example Code Structure

```python
"""
Module docstring explaining the purpose.
"""

from typing import Optional
import discord
from discord.ext import commands


class ExampleCog(commands.Cog):
    """Example cog demonstrating coding standards."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.slash_command(name="example")
    async def example_command(
        self, 
        ctx: discord.ApplicationContext,
        parameter: str
    ) -> None:
        """
        Example slash command.
        
        Args:
            ctx: Discord application context
            parameter: Example parameter
        """
        try:
            # Command logic here
            await ctx.respond(f"Example response: {parameter}")
        except Exception as e:
            await ctx.respond(f"Error: {e}", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(ExampleCog(bot))
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=gitcord

# Run specific test file
python -m pytest tests/test_specific_module.py
```

### Writing Tests

- Write tests for new functionality
- Use descriptive test names
- Mock external dependencies (Discord API, GitHub API)
- Aim for good test coverage

### Example Test

```python
"""Test example cog functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import discord
from gitcord.cogs.example import ExampleCog


@pytest.fixture
def mock_context():
    """Create a mock Discord context."""
    context = MagicMock(spec=discord.ApplicationContext)
    context.respond = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_example_command(mock_context):
    """Test the example command."""
    bot = MagicMock()
    cog = ExampleCog(bot)
    
    await cog.example_command(mock_context, "test_parameter")
    
    mock_context.respond.assert_called_once_with(
        "Example response: test_parameter"
    )
```

## Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Follow Google or NumPy docstring format
- Include type hints
- Document exceptions that may be raised

### README Updates

- Update README.md for significant changes
- Keep installation instructions current
- Document new features and configuration options

### API Documentation

- Document Discord bot commands and their usage
- Explain configuration file formats
- Provide examples for common use cases

## Issue Guidelines

### Before Creating an Issue

1. Check existing issues for duplicates
2. Search the documentation for solutions
3. Try to reproduce the issue locally

### Issue Template

When creating an issue, include:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of the problem
- **Steps to Reproduce**: Step-by-step instructions
- **Expected vs Actual Behavior**: What you expected vs what happened
- **Environment**: Python version, OS, Discord.py version
- **Additional Context**: Screenshots, logs, etc.

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed

## Pull Request Guidelines

### Before Submitting

1. Ensure all tests pass
2. Update documentation if needed
3. Follow the coding standards
4. Test your changes thoroughly

### PR Template

- **Title**: Clear, descriptive title
- **Description**: Explain what the PR does and why
- **Related Issues**: Link to related issues
- **Type of Change**: Bug fix, feature, documentation, etc.
- **Testing**: How you tested your changes
- **Checklist**: Ensure all requirements are met

### PR Review Process

1. Automated checks must pass (linting, tests)
2. Code review by maintainers
3. Address feedback and make requested changes
4. Maintainers will merge when approved

## Release Process

### Versioning

This project follows [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Current version: `0.6.0` (Alpha)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped in `pyproject.toml`
- [ ] Release notes are prepared

## Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

### Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## License

By contributing to GitCord, you agree that your contributions will be licensed under the GNU General Public License v3.0.

---

Thank you for contributing to GitCord! Your contributions help make this project better for everyone. 