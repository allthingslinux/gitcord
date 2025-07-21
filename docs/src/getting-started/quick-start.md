# Quick Start

Get GitCord working in minutes!

> **Note:** These instructions are for the current version of GitCord. Once GitHub integration is implemented, the setup and usage steps will change dramatically. Please check back for updated instructions in future releases.


## What You Need

- GitCord bot running (see [Installation](./installation.md))
- Bot has permissions in your Discord server
- You have admin permissions

## Step 1: Create a Channel

Create a file called `general.yaml`:

```yaml
name: general
type: text
topic: General discussion for the server
position: 0
nsfw: false
```

## Step 2: Create the Channel

In your Discord server, use:

```
!createchannel
```

**Note:** This command uses a fixed file path. You'll need to put your file in the right place.

## Step 3: Create Multiple Channels

Create a category file:

```yaml
# category.yaml
name: community
type: category
position: 0

channels:
  - general
  - announcements
  - voice-chat
```

Then create channel files for each channel listed.

## Step 4: Create the Category

Use:

```
!createcategory
```

Or with a specific path:

```
/createcategory path/to/category.yaml
```

## Step 5: Try Basic Commands

```
!hello          # Get a greeting
!ping           # Check bot latency
!help           # Show help information
```

## Example Templates

### Community Category
```yaml
# category.yaml
name: community
type: category
position: 0

channels:
  - general
  - announcements
  - memes
  - off-topic
```

### Voice Category
```yaml
# category.yaml
name: voice-chats
type: category
position: 1

channels:
  - vc1
  - vc2
```

## Next Steps

- Learn about [Channel Management](../user-guide/channel-management.md)
- Explore [Categories](../user-guide/categories.md)
- Check [Available Commands](../user-guide/commands.md)
- Read about [Permissions](../user-guide/permissions.md)

## Tips

- Use clear, simple names
- Test your YAML files first
- Keep backups of your files
- Use the `!help` command for more options 