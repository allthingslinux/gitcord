# [GitCord](https://evolvewithevan.github.io/gitcord/troubleshooting/debug-mode.html)

[![Documentation](https://img.shields.io/badge/docs-mdBook-blue)](https://evolvewithevan.github.io/gitcord/)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)

GitCord is a Discord bot that allows you to manage your Discord server's channel structure and configuration through Git. It provides a seamless way to version control your Discord server setup and automatically sync changes from your GitHub repository.

## ⚠️ Disclaimer

**This project is currently in early development and does not have a complete featureset yet.** The bot exists as a basic framework, but some core functionality described in this README is not yet implemented. 
**Do not run this on servers with untrusted members present. It is not secure yet.**

We have detailed plans and are actively working on bringing these features to life. Check back soon for updates, or feel free to contribute to help accelerate development.

## Getting Started

To get started in using **GitCord**, you can either design your own server channel structure from scratch or fork the **[gitcord-template](https://github.com/evolvewithevan/gitcord-template)**. This template provides a sample structure that demonstrates how to define your server's categories and channels using organized YAML configuration files.

Once it's ready, you'll have to link the **GitCord** bot to your own repository, finally, you will be able to discuss and organize your Discord server all in a transparent, team-friendly GitHub repository. To manually synchronize with your repository, you can run `/gitcord pull` on the server.


## Planned Features

This list is incomplete, See (all issues)[https://github.com/users/evolvewithevan/projects/4/views/1?pane=info] to see a complete list of all issues or (Feature Issues)[https://github.com/users/evolvewithevan/projects/4/views/8?pane=info] to see feature updates planned. 
- [ ] **Version-Controlled Configuration**: Store your Discord server configuration in a Git repository
- [ ] **Automatic Sync**: Webhook-based synchronization when configuration changes are pushed to GitHub
- [ ] **Manual Pull**: Use `/gitcord pull` command to manually sync configuration changes
- [x] **Command Syncing**: Use `/synccommands` (slash) or `!synccommands` (prefix) to manually synchronize slash commands
- [x] **Category and Channel Management**: Organize your server structure through YAML configuration files

## Project Status

This project is currently in development. See the [roadmap](https://github.com/users/evolvewithevan/projects/4) for current development status and planned features.

### Current Development Phase

- **Prototype Phase**: Basic Discord bot with manual pull functionality

## Contributing

Please see our [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for contribution guidelines 

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

We aim to personally respond to every PR within 24hr

## License

This project is and will remain licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

For detailed development plans and current status, see the [roadmap](https://github.com/users/evolvewithevan/projects/4/views/3?pane=info) and [status-updates](https://github.com/users/evolvewithevan/projects/4/views/3?pane=info&statusUpdateId=134528)

## Support

If you encounter any issues or have questions, please open an issue on this GitHub repository or open a Discussion page. We aim to respond within 24hr.

---

Made with ❤️ by the GitCord Team. [Full Documentation](https://evolvewithevan.github.io/gitcord/)
