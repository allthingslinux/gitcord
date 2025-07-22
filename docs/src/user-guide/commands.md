# Commands

GitCord has commands for managing your Discord server. You can use `!` commands or `/` slash commands.

## Basic Commands

### `!hello`
Say hello to the bot.

**Usage:** `!hello`

**Permissions:** None needed

### `!ping` / `/slashping`
Check if the bot is working.

**Usage:** 
- `!ping`
- `/slashping`

**Permissions:** None needed

## Channel Commands

### `!createchannel`
Create one channel from a YAML file.

**Usage:** `!createchannel`

**Permissions:** Manage Channels

**Note:** Now uses dynamic template paths. For servers using the new monolithic template format, this command shows a deprecation warning and suggests using `!git pull` instead. 

### `!createcategory` / `/createcategory`
Create a category with multiple channels.

**Usage:**
- `!createcategory`
- `/createcategory [yaml_path]`

**Permissions:** Manage Channels

**Note:** `!createcategory` uses a fixed path by default, This will be changed with the release of 1.X. `/createcategory` lets you specify a path.

## Admin Commands

### `!fetchurl` / `/fetchurl`
Get text from a website.

**Usage:**
- `!fetchurl <url>`
- `/fetchurl <url>`

**Permissions:** Administrator

### `!synccommands` / `/synccommands`
Update slash commands.

**Usage:**
- `!synccommands`
- `/synccommands`

**Permissions:** Administrator

## Help Commands

### `!help` / `/help`
Show help and links.

**Usage:**
- `!help`
- `/help`

**Permissions:** None needed

## Permissions

- **None needed:** Anyone can use
- **Manage Channels:** Can create/edit channels
- **Administrator:** Can use admin commands

## Common Errors

- **"Command not found"**: Check spelling or sync commands
- **"Permission denied"**: You need the right permissions
- **"File not found"**: Check your YAML file path
