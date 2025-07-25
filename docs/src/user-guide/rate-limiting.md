# Rate Limiting

GitCord includes a built-in rate limiting system to prevent abuse and ensure stable operation. This system limits how frequently all users can execute bot commands.

## How It Works

The rate limiting system:
- Limits all users to **1 command per 5 seconds**
- Applies equally to all users including administrators
- Shows friendly error messages when limits are exceeded
- Is always enabled and cannot be disabled

## Rate Limit Configuration

Rate limiting is **hard-coded** and cannot be configured:
- **Limit**: 1 command per 5 seconds
- **Always enabled**: Cannot be turned off
- **Applies to everyone**: No exemptions for any users

## Rate Limit Messages

When any user hits the rate limit, they'll see a message like:

> ⏰ **Rate Limited**
> 
> You're sending commands too quickly! Please wait **3.2s** before trying again.
> 
> **Rate Limit:** 1 command(s) per 5 seconds

Rate limit messages:
- Auto-delete after 10 seconds to reduce spam
- Only appear once every 30 seconds per user
- Are ephemeral for slash commands

## Implementation Details

### For Developers

Rate limiting is implemented using decorators that are applied to all commands:

```python
from ..utils.rate_limiter import rate_limit, rate_limit_app_command

# For prefix commands
@rate_limit()
@commands.command(name="mycommand")
async def my_command(self, ctx):
    # Command logic here

# For slash commands  
@rate_limit_app_command()
@app_commands.command(name="myslashcommand")
async def my_slash_command(self, interaction):
    # Command logic here
```

### Rate Limiting Strategy

The system uses a **sliding window** approach:
- Tracks timestamps of recent commands per user
- Removes timestamps outside the current window
- Blocks commands when the limit is exceeded
- Calculates precise time until next allowed command

### Memory Management

The rate limiter automatically cleans up old data:
- Timestamps older than the window are removed
- Unused user data doesn't accumulate indefinitely
- Memory usage remains constant under normal operation

## Why Rate Limiting Applies to Everyone

Rate limiting applies to all users equally, including administrators, for several reasons:

1. **Fairness**: Ensures all users follow the same rules
2. **Consistency**: Prevents accidental command spam from any user
3. **Simplicity**: No complex permission checking or configuration
4. **Protection**: Guards against both malicious and accidental abuse

## Best Practices

### For Server Administrators
- Understand that rate limiting protects your server's stability
- Be mindful of command frequency when performing administrative tasks
- Plan bulk operations with the 5-second delay in mind

### For Users
- Space out your commands naturally during normal usage
- Wait for the rate limit to reset before trying failed commands again
- Use slash commands when possible for a better user experience

## Troubleshooting

### "I'm getting rate limited as an admin"
This is expected behavior. Rate limiting applies to all users equally to ensure fairness and server stability.

### "The rate limit is too restrictive"
The 1 command per 5 seconds limit is designed to prevent abuse while allowing normal usage. Most legitimate use cases work well within this limit.

### "Can I disable rate limiting for my server?"
No, rate limiting is always enabled and cannot be disabled. This ensures consistent protection across all GitCord installations.

### "Can I increase the rate limit?"
Rate limits are hard-coded and cannot be modified without changing the bot's source code. This ensures consistent behavior and prevents misuse.

## Technical Details

- **Algorithm**: Sliding window with timestamp tracking
- **Limit**: 1 command per 5 seconds (hard-coded)
- **Scope**: Per-user, global across all commands
- **Storage**: In-memory using Python deques
- **Cleanup**: Automatic removal of expired timestamps