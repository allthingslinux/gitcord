# Permissions

GitCord uses Discord's permission system. You need different permissions for different commands.

## Permission Levels

### No Permissions Needed
Anyone can use these commands:
- `!hello` - Say hello
- `!ping` / `/slashping` - Check if bot works
- `!help` / `/help` - Show help

### Manage Channels
You need "Manage Channels" permission for:
- `!createchannel` - Create channels
- `!createcategory` / `/createcategory` - Create categories

### Administrator
You need "Administrator" permission for:
- `!fetchurl` / `/fetchurl` - Get text from websites
- `!synccommands` / `/synccommands` - Update slash commands

## Setting Up Permissions

### For Server Admins
1. Create roles for different permission levels
2. Give "Manage Channels" to moderators
3. Give "Administrator" only to trusted admins
4. Test with different user accounts

### Recommended Roles
```
Server Owner (Administrator)
├── Bot Admin (Administrator)
├── Moderator (Manage Channels)
└── Member (No special permissions)
```

## Security Tips

- Only give permissions that are needed
- Regularly check who has what permissions
- Remove permissions when people don't need them
- Use roles instead of individual permissions

## Common Issues

- **"Permission denied"**: You need the right permission
- **"Bot can't do that"**: Bot needs the right permissions
- **"Role hierarchy"**: Bot's role must be above roles it manages
