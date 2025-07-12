#!/usr/bin/env python3
"""
Environment setup script for GitCord bot.
This script helps you create the necessary .env file with your Discord bot token.
"""

import os


def create_env_file():
    """Create .env file with user input."""
    print("=== GitCord Bot Setup ===")
    print("This script will help you create the .env file with your Discord bot token.")
    print()

    # Check if .env already exists
    if os.path.exists('.env'):
        print("Warning: .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return

    # Get Discord token from user
    print("Please enter your Discord bot token:")
    print("(You can get this from https://discord.com/developers/applications)")
    print()

    token = input("Discord Bot Token: ").strip()

    if not token:
        print("Error: Token cannot be empty!")
        return

    # Create .env file
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"DISCORD_TOKEN={token}\n")

        print()
        print("✅ .env file created successfully!")
        print("You can now run the bot with: python main.py")

    except Exception as e:
        print(f"Error creating .env file: {e}")


def main():
    """Main setup function."""
    create_env_file()


if __name__ == "__main__":
    main()
