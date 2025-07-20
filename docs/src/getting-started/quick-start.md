# Quick Start

Get up and running with GitCord in minutes! This guide will show you how to create your first channels using templates.

## Prerequisites

- GitCord bot installed and running (see [Installation](./installation.md))
- Bot has proper permissions in your Discord server
- You have administrator permissions in the server

## Step 1: Create a Simple Channel Template

Create a file called `my-channels.yaml` with this content:

```yaml
name: general
type: text
topic: General discussion for the server
position: 0
```

## Step 2: Use the Create Command

In your Discord server, use the slash command:

```
/create-channel
```

Then upload your `my-channels.yaml` file when prompted.

## Step 3: Create Multiple Channels

Create a more complex template with multiple channels:

```yaml
name: community
type: category
channels:
  - name: general
    type: text
    topic: General discussion
  - name: announcements
    type: text
    topic: Important announcements
  - name: voice-chat
    type: voice
    topic: Voice chat room
```

Use the same `/create-channel` command with this template.

## Step 4: Explore Built-in Templates

GitCord comes with pre-built templates. Try:

```
/templates list
```

This shows available templates you can use immediately.

## Step 5: Use a Template

To use a built-in template:

```
/templates use community
```

This creates a community category with general channels.

## Common Templates

### Community Template
```yaml
name: community
type: category
channels:
  - name: general
    type: text
    topic: General discussion
  - name: announcements
    type: text
    topic: Important announcements
  - name: memes
    type: text
    topic: Share your memes here
  - name: off-topic
    type: text
    topic: Off-topic discussions
```

### Gaming Template
```yaml
name: gaming
type: category
channels:
  - name: general-gaming
    type: text
    topic: General gaming discussion
  - name: voice-chat
    type: voice
    topic: Gaming voice chat
  - name: game-announcements
    type: text
    topic: Game updates and announcements
```

## Next Steps

- Learn about [Channel Management](../user-guide/channel-management.md)
- Explore [Configuration](./configuration.md) options
- Check out [Available Commands](../user-guide/commands.md)
- Create [Custom Templates](../templates/custom-templates.md)

## Tips

- Use descriptive channel names and topics
- Organize channels into categories for better structure
- Test templates in a private server first
- Use the `/help` command to see all available options 