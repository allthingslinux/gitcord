# GitCord

A Discord bot that integrates with GitHub to manage Discord server configurations through version-controlled configuration files.

## Overview

GitCord is a Discord bot that allows you to manage your Discord server's channel structure and configuration through Git. It provides a seamless way to version control your Discord server setup and automatically sync changes from your GitHub repository.

## ⚠️ Disclaimer

**This project is currently in early development and does not have any functional features yet.** The bot exists as a basic framework, but the core functionality described in this README is not yet implemented. 

We have detailed plans and are actively working on bringing these features to life. Code is on the way! Check back soon for updates, or feel free to contribute to help accelerate development.


## Planned Features

- **Version-Controlled Configuration**: Store your Discord server configuration in a Git repository
- **Automatic Sync**: Webhook-based synchronization when configuration changes are pushed to GitHub
- **Manual Pull**: Use `/gitcord pull` command to manually sync configuration changes
- **Category and Channel Management**: Organize your server structure through YAML configuration files

## Project Status

This project is currently in development. See the [roadmap](./roadmap/) for current development status and planned features.

### Current Development Phase

- **POC Phase**: Basic Discord bot with manual pull functionality

## Architecture

### Configuration Structure

```
servermap/
├── category1/
│   ├── category.yaml
│   ├── channel1.yaml
│   └── channel2.yaml
├── category2/
│   ├── category.yaml
│   └── channel3.yaml
└── ...
```

### Planned Components

- **Discord Bot**: Built with Discord.py, handles slash commands and server management
- **Webhook Server**: Flask-based server to receive GitHub webhook events
- **Configuration Parser**: Processes yaml configuration files to apply Discord server changes

## Planned Features

### POC Phase
- [ ] Create hello world bot on Discord side
- [ ] Bot pulls from `/servermap/` to apply channel configuration upon a `/gitcord pull` command
  - Categories will be placed within subdirs of `/servermap/`
  - Each category will be described via a `category.yaml` file
  - Within a category's subdir, each channel will be described via a `channelname.yaml`

## Development

### Project Structure
```
gitcord/
├── roadmap/          # Development roadmap and planning
├── LICENSE          # GNU GPL v3 License
└── README.md        # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

For detailed development plans and current status, see the [roadmap](./roadmap/) directory:
- [POC Development Plan](./roadmap/poc.md)
- [Prototype Development Plan](./roadmap/prototype.md)

## Support

If you encounter any issues or have questions, please open an issue on this GitHub repository.

---

**Note**: This project is currently in active development. Features and documentation may change as the project evolves. 