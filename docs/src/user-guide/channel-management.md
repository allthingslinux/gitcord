# Channel Management

GitCord lets you create Discord channels using YAML files. This makes it easy to set up your server the same way every time.

## How It Works

1. Write a YAML file describing your channel
2. Use a command to create the channel
3. GitCord reads the file and makes the channel

## Channel Types

### Text Channels
For typing messages.

```yaml
name: general
type: text
position: 0
topic: "General chat for everyone"
nsfw: false
```

### Voice Channels
For talking with voice.

```yaml
name: General Voice
type: voice
position: 0
user_limit: 10
```

### Categories
Groups that hold other channels.

```yaml
name: Community
position: 0
type: category

channels:
  - general
  - memes
  - off-topic
```

## Creating Channels

### Single Channel
Use `!createchannel` to make one channel.

**Note:** This command uses a fixed file path.

### Multiple Channels
Use `!createcategory` or `/createcategory` to make a category with channels.

1. Create a category YAML file
2. Create channel YAML files for each channel
3. Run the command

## YAML Basics

### Required Fields
- `name`: Channel name
- `type`: "text", "voice", or "category"
- `position`: Where it appears (0 = top)

### Optional Fields
- `topic`: Channel description
- `nsfw`: Set to true for NSFW channels
- `user_limit`: Max users in voice channels

## Tips

- Use simple, clear names
- Test your YAML files first
- Keep backups of your files
- Use categories to organize channels
