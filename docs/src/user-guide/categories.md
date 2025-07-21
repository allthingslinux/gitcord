# Categories

Categories group related channels together in Discord. GitCord lets you create categories using YAML files.

## What Are Categories?

Categories are folders that hold channels. They help organize your server and make it look cleaner.

## Creating Categories

### Basic Category
```yaml
name: Community
position: 0
type: category

channels:
  - general
  - memes
  - off-topic
```

### Required Fields
- `name`: Category name
- `position`: Where it appears (0 = top)
- `type`: Must be "category"
- `channels`: List of channel files (without .yaml)

## How to Use

1. Create a category YAML file
2. Create channel YAML files for each channel
3. Run `!createcategory` or `/createcategory`

## Examples

### Community Category
```yaml
# community.yaml
name: Community
position: 0
type: category

channels:
  - general
  - memes
  - off-topic
```

### Voice Category
```yaml
# voice.yaml
name: Voice Chats
position: 1
type: category

channels:
  - vc1
  - vc2
```

## Channel Files

Each channel listed in the category needs its own YAML file:

```yaml
# general.yaml
name: general
type: text
position: 0
topic: "General chat for everyone"
```

## Tips

- Use clear, simple names
- Position categories logically
- Keep related channels together
- Test your setup first
