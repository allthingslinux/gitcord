# Category Templates

Category templates in GitCord allow you to create standardized category configurations that group related channels together. This guide covers how to create, use, and manage category templates.

## What are Category Templates?

Category templates are YAML configuration files that define Discord categories and their associated channels. They provide a structured way to organize server content by grouping related channels together under logical categories.

## Template Structure

### Basic Category Template

<details>
<summary>Basic Category Template Example</summary>

A category template consists of a YAML file with category configuration:

```yaml
name: Community
position: 0
type: category

channels:
  - general
  - introductions
  - memes
  - off-topic
```

</details>

### Required Fields

Every category template must include these fields:

- **`name`**: The display name of the category
- **`position`**: The position of the category in the server sidebar (0 = top)
- **`type`**: Must be "category"
- **`channels`**: List of channel file names (without .yaml extension)

### Optional Fields

<details>
<summary>Optional Fields Example</summary>

You can include additional fields for advanced configuration:

```yaml
name: Community
position: 0
type: category
description: "Community discussion channels"

channels:
  - general
  - introductions
  - memes
  - off-topic

# Advanced options (future features)
permissions:
  - role: "@everyone"
    allow: ["view_channel", "send_messages"]
  - role: "Moderator"
    allow: ["manage_messages"]
```

</details>

## Creating Category Templates

### Step 1: Plan Your Category

Before creating a template, consider:

1. **Purpose**: What is the category for?
2. **Channels**: What channels should be included?
3. **Organization**: How should channels be ordered?
4. **Permissions**: What permissions should be set?

### Step 2: Create Channel Templates

<details>
<summary>Channel Template Example: general.yaml</summary>

First, create individual channel templates for each channel in the category:

```yaml
# general.yaml
name: general
type: text
position: 0
topic: "General chat for everyone"
nsfw: false
```

</details>

<details>
<summary>Channel Template Example: introductions.yaml</summary>

```yaml
# introductions.yaml
name: introductions
type: text
position: 1
topic: "Introduce yourself to the community!"
nsfw: false
```

</details>

### Step 3: Create Category Template

<details>
<summary>Category Template Example: community.yaml</summary>

Create the category template that references the channel files:

```yaml
# community.yaml
name: Community
position: 0
type: category

channels:
  - general
  - introductions
  - memes
  - off-topic
```

</details>

### Step 4: Test Your Template

Test your category template:

1. **Validate YAML syntax** using a YAML validator
2. **Ensure all channel files exist** and are valid
3. **Test in a development server** first
4. **Check channel ordering** and positioning

## Template Examples

<details>
<summary>Community Category Example</summary>

A typical community category with discussion channels:

```yaml
# community.yaml
name: Community
position: 0
type: category

channels:
  - general
  - introductions
  - memes
  - off-topic
  - suggestions
```

**Associated Channel Files:**
- `general.yaml` - Main chat channel
- `introductions.yaml` - New member introductions
- `memes.yaml` - Memes and humor
- `off-topic.yaml` - Random discussions
- `suggestions.yaml` - Community suggestions

</details>

<details>
<summary>Voice Channels Category Example</summary>

A category for voice communication:

```yaml
# voice.yaml
name: Voice Channels
position: 1
type: category

channels:
  - general-voice
  - gaming
  - music
  - chill
```

**Associated Channel Files:**
- `general-voice.yaml` - General voice chat
- `gaming.yaml` - Gaming voice channel
- `music.yaml` - Music listening
- `chill.yaml` - Relaxed voice chat

</details>

<details>
<summary>Administrative Category Example</summary>

A category for server administration:

```yaml
# admin.yaml
name: Administrative
position: 2
type: category

channels:
  - announcements
  - rules
  - staff-chat
  - logs
```

**Associated Channel Files:**
- `announcements.yaml` - Server announcements
- `rules.yaml` - Server rules
- `staff-chat.yaml` - Staff discussions
- `logs.yaml` - Bot logs

</details>

<details>
<summary>Gaming Category Example</summary>

A category for gaming-related channels:

```yaml
# gaming.yaml
name: Gaming
position: 3
type: category

channels:
  - general-gaming
  - minecraft
  - valorant
  - league-of-legends
  - gaming-news
```

**Associated Channel Files:**
- `general-gaming.yaml` - General gaming discussion
- `minecraft.yaml` - Minecraft-specific chat
- `valorant.yaml` - Valorant discussion
- `league-of-legends.yaml` - LoL discussion
- `gaming-news.yaml` - Gaming news and updates

</details>

## Using Category Templates

### Single Category Creation

Use the `!createcategory` or `/createcategory` command:

1. **Run the command**: `!createcategory` or `/createcategory`
2. **Provide the template path**: Enter the path to your category YAML file
3. **Review the results**: Check the bot's response for success/errors

### Multiple Categories

<details>
<summary>Multiple Category Creation Example (Bash)</summary>

Create multiple categories by running the command for each:

```bash
# Create community category
!createcategory community.yaml

# Create voice category
!createcategory voice.yaml

# Create admin category
!createcategory admin.yaml
```

</details>

### Template Organization

<details>
<summary>Template Organization Example</summary>

Organize your templates logically:

```
templates/
├── categories/
│   ├── community.yaml
│   ├── voice.yaml
│   ├── admin.yaml
│   └── gaming.yaml
└── channels/
    ├── community/
    │   ├── general.yaml
    │   ├── introductions.yaml
    │   └── memes.yaml
    ├── voice/
    │   ├── general-voice.yaml
    │   └── gaming.yaml
    └── admin/
        ├── announcements.yaml
        └── rules.yaml
```

</details>

## Advanced Templates

<details>
<summary>Conditional Channels Example</summary>

Create templates that adapt based on server needs:

```yaml
# flexible-community.yaml
name: Community
position: 0
type: category

channels:
  - general
  - introductions
  # Optional channels based on server size
  - memes          # For larger servers
  - off-topic      # For larger servers
  - suggestions    # For active communities
```

</details>

<details>
<summary>Template Inheritance Example</summary>

Create base templates that can be extended:

```yaml
# base-category.yaml
type: category
description: "Base category template"

# community.yaml (extends base-category.yaml)
name: Community
position: 0
channels:
  - general
  - introductions
```

</details>

<details>
<summary>Dynamic Positioning Example</summary>

Use relative positioning for flexible layouts:

```yaml
# community.yaml
name: Community
position: 0
type: category

channels:
  - general        # position: 0
  - introductions  # position: 1
  - memes          # position: 2
  - off-topic      # position: 3
```

</details>

## Best Practices

### Naming Conventions

1. **Use descriptive names**: Make category purposes clear
2. **Use consistent naming**: Follow a pattern across categories
3. **Avoid special characters**: Stick to letters, numbers, and spaces
4. **Keep names concise**: But informative

### Organization

1. **Group related channels**: Put similar channels together
2. **Use logical positioning**: Order categories by importance
3. **Consider user experience**: Make navigation intuitive
4. **Plan for growth**: Leave room for future categories

### Channel Management

1. **Limit channels per category**: Don't overload categories
2. **Use consistent channel ordering**: Within categories
3. **Set appropriate permissions**: For category and channels
4. **Regular maintenance**: Update categories as needed

## Template Validation

### YAML Syntax

<details>
<summary>YAML Syntax Validation Example</summary>

Ensure your YAML is valid:

```yaml
# Valid YAML
name: Community
position: 0
type: category

channels:
  - general
  - introductions

# Invalid YAML (incorrect indentation)
name: Community
position: 0
type: category
channels:
- general
- introductions
```

</details>

### Required Fields

<details>
<summary>Missing Required Field Example</summary>

Check that all required fields are present:

```yaml
# Missing required field 'channels'
name: Community
position: 0
type: category
# This will cause an error
```

</details>

### Channel File References

<details>
<summary>Channel File Reference Example</summary>

Ensure all referenced channel files exist:

```yaml
# community.yaml
name: Community
position: 0
type: category

channels:
  - general        # Requires general.yaml
  - introductions  # Requires introductions.yaml
  - nonexistent    # This will cause an error
```

</details>

## Troubleshooting

### Common Issues

1. **"Invalid YAML" errors**:
   - Check YAML syntax and indentation
   - Use a YAML validator
   - Ensure proper field structure

2. **"Missing required field" errors**:
   - Verify all required fields are present
   - Check field names for typos
   - Ensure proper field hierarchy

3. **"Channel file not found" errors**:
   - Check that all channel files exist
   - Verify file paths are correct
   - Ensure channel files are valid YAML

4. **"Category already exists" errors**:
   - Check if category name conflicts
   - Use unique names for categories
   - Consider using the update feature

### Debug Tips

1. **Test with simple templates** first
2. **Use YAML validators** to check syntax
3. **Check file paths** are correct
4. **Review bot logs** for detailed errors
5. **Test in development** before production

## Template Sharing

### Version Control

<details>
<summary>Version Control Example (Bash)</summary>

Store templates in version control:

```bash
# Add templates to git
git add templates/
git commit -m "Add category templates"
git push origin main
```

</details>

### Template Repositories

Share templates with the community:

1. **Create a template repository**
2. **Document your templates**
3. **Provide examples**
4. **Accept contributions**

### Template Standards

Follow community standards:

1. **Use consistent naming**
2. **Include documentation**
3. **Provide examples**
4. **Test thoroughly**

## Server Structure Examples

<details>
<summary>Server Structure: Small Community</summary>

```
📁 Community (0)
  ├── # general
  ├── # introductions
  └── # off-topic

📁 Voice Channels (1)
  ├── 🔊 General Voice
  └── 🔊 Gaming Voice

📁 Administrative (2)
  ├── # announcements
  └── # rules
```

</details>

<details>
<summary>Server Structure: Medium Gaming</summary>

```
📁 Community (0)
  ├── # general
  ├── # introductions
  ├── # memes
  └── # off-topic

📁 Gaming (1)
  ├── # general-gaming
  ├── # minecraft
  ├── # valorant
  └── # gaming-news

📁 Voice Channels (2)
  ├── 🔊 General Voice
  ├── 🔊 Gaming Voice
  └── 🔊 Music Voice

📁 Administrative (3)
  ├── # announcements
  ├── # rules
  └── # staff-chat
```

</details>

<details>
<summary>Server Structure: Large Community</summary>

```
📁 Community (0)
  ├── # general
  ├── # introductions
  ├── # memes
  ├── # off-topic
  └── # suggestions

📁 Gaming (1)
  ├── # general-gaming
  ├── # minecraft
  ├── # valorant
  ├── # league-of-legends
  └── # gaming-news

📁 Voice Channels (2)
  ├── 🔊 General Voice
  ├── 🔊 Gaming Voice
  ├── 🔊 Music Voice
  └── 🔊 Chill Voice

📁 Events (3)
  ├── # events
  ├── # event-voice
  └── # event-announcements

📁 Administrative (4)
  ├── # announcements
  ├── # rules
  ├── # staff-chat
  └── # logs
```

</details>

## Future Enhancements

### Planned Features

1. **Category Permissions**: Set permissions at category level
2. **Template Variables**: Dynamic category values
3. **Template Inheritance**: Base category extension
4. **Category Nesting**: Nested category support
5. **Category Templates**: Reusable category patterns

### Extension Points

1. **Custom Category Types**: Support for new category features
2. **Advanced Properties**: More category configuration options
3. **Category Macros**: Reusable category components
4. **Category Import/Export**: Category sharing mechanisms
5. **Category Preview**: Visual category previews
