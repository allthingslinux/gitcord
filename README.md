# GitCord

A Discord bot for GitOps-based Discord server management. Manage your server's channels and categories using YAML templates, version control, and GitHub integration.

[![Documentation](https://img.shields.io/badge/docs-mdBook-blue)](https://evolvewithevan.github.io/gitcord/)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)

---

## 🚀 Getting Started

### Option 1: Use Pre-Hosted Bot (Recommended)

The easiest way to get started is to invite the pre-hosted GitCord bot to your Discord server:

**[📥 Invite GitCord Bot](https://discord.com/oauth2/authorize?client_id=1391153955936927824)**

After inviting the bot, you can start using commands immediately. See the [Quick Start Guide](https://evolvewithevan.github.io/gitcord/getting-started/quick-start.html) for usage examples.

### Option 2: Self-Host (Advanced Users)

If you prefer to run your own instance of GitCord:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/evolvewithevan/gitcord.git
   cd gitcord
   ```
2. **Install dependencies (requires Python 3.9+ and [uv](https://github.com/astral-sh/uv))**
   ```bash
   uv sync
   ```
3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord bot token
   ```
4. **Run the bot:**
   ```bash
   python -m gitcord
   ```

For detailed self-hosting setup, see the [Installation Guide](https://evolvewithevan.github.io/gitcord/getting-started/installation.html).

---

## 📝 What is GitCord?

GitCord is a Discord bot that lets you manage your server's structure using YAML configuration files, stored in Git and optionally synced with GitHub. It enables:
- **Version-controlled server configuration**
- **Automated and manual sync of categories/channels**
- **Bulk creation of channels/categories from templates**
- **Easy server setup and reproducibility**

---

## ✨ Features
- **Template-based Channel & Category Creation**: Use YAML files to define your server structure
- **Manual & Planned Automatic Sync**: Pull changes from a GitHub repo or local files
- **Slash & Prefix Commands**: Use `/createcategory`, `/createchannel`, `!createcategory`, etc.
- **Permission Management**: Follows Discord's permission system
- **Extensible**: Modular cog system for easy extension
- **Open Source**: GPL-3.0 License

See the [full feature list](https://evolvewithevan.github.io/gitcord/introduction.html#key-features).

---

## 🛠️ Example Usage

- **Create a channel from YAML:**
  ```yaml
  # general.yaml
  name: general
  type: text
  topic: General discussion
  position: 0
  nsfw: false
  ```
  Use: `!createchannel`

- **Create a category with channels:**
  ```yaml
  # community.yaml
  name: Community
  type: category
  position: 0
  channels:
    - general
    - memes
    - off-topic
  ```
  Use: `!createcategory` or `/createcategory`

See [Quick Start](https://evolvewithevan.github.io/gitcord/getting-started/quick-start.html) and [Templates Guide](https://evolvewithevan.github.io/gitcord/templates/category-templates.html).

---

## 🧩 Main Commands

- `!hello` / `/hello` — Greet the bot
- `!ping` / `/slashping` — Check bot latency
- `!createchannel` — Create a channel from YAML
- `!createcategory` / `/createcategory [yaml_path]` — Create a category with channels
- `!fetchurl <url>` / `/fetchurl <url>` — Fetch text from a website (admin)
- `!synccommands` / `/synccommands` — Update slash commands (admin)
- `!help` / `/help` — Show help and links

See [Commands Reference](https://evolvewithevan.github.io/gitcord/user-guide/commands.html).

---

## 📁 Project Structure

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
├── gitcord-template/     # Example template repository
├── docs/                 # Documentation (mdBook)
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md             # Project documentation
```

---

## 📈 Project Status & Roadmap

- **Alpha**: Core features implemented, active development
- See the [Roadmap](https://github.com/users/evolvewithevan/projects/4) for planned features and progress
- [Planned Features](https://evolvewithevan.github.io/gitcord/templates/category-templates.html#future-enhancements):
  - Webhook-based automatic sync
  - Advanced template features (inheritance, variables)
  - More admin tools

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Coding standards (PEP8, type hints, docstrings)
- How to set up your dev environment
- Testing and documentation guidelines
- Pull request process

---

## 🆘 Support & Troubleshooting

- [Common Issues](https://evolvewithevan.github.io/gitcord/troubleshooting/common-issues.html)
- [Error Messages](https://evolvewithevan.github.io/gitcord/troubleshooting/error-messages.html)
- [GitHub Issues](https://github.com/evolvewithevan/gitcord/issues)
- [Discussions](https://github.com/evolvewithevan/gitcord/discussions)

---

## 📜 License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).

---

Made with ❤️ by the GitCord Team. [Full Documentation](https://evolvewithevan.github.io/gitcord/)
