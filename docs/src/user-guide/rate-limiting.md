# Rate Limiting

GitCord includes a built-in rate limiting system to prevent abuse and ensure stable operation. This system limits how frequently users can execute bot commands.

## How It Works

The rate limiting system:
- Limits users to **1 command per 5 seconds** by default
- Automatically exempts users with administrative permissions
- Shows friendly error messages when limits are exceeded
- Can be configured via environment variables

## Exempt Users

The following users are automatically exempt from rate limiting:
- Users with **Administrator** permission
- Users with **Manage Guild** permission  
- Users with **Manage Channels** permission

## Configuration

Rate limiting can be configured using environment variables:

```bash
# Enable/disable rate limiting (default: true)
RATE_LIMIT_ENABLED=true

# Maximum commands per time window (default: 1)
RATE_LIMIT_MAX_COMMANDS=1

# Time window in seconds (default: 5)
RATE_LIMIT_WINDOW=5
```

## Admin Commands

Administrators can manage rate limiting using the `!ratelimit` command:

### View Current Configuration
```
!ratelimit status
```

### View User Statistics
```
!ratelimit stats @username
```

### Enable/Disable Rate Limiting
```
!ratelimit enable
!ratelimit disable
```

## Rate Limit Messages

When a user hits the rate limit, they'll see a message like:

> ⏰ **Rate Limited**
> 
> You're sending commands too quickly! Please wait **3.2s** before trying again.
> 
> **Rate Limit:** 1 command(s) per 5 seconds
> *Admins and moderators are exempt from rate limiting.*

Rate limit messages:
- Auto-delete after 10 seconds to reduce spam
- Only appear once every 30 seconds per user
- Are ephemeral for slash commands

## Implementation Details

### For Developers

Rate limiting is implemented using decorators that can be applied to any command:

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

## Troubleshooting

### Rate Limiting Not Working
1. Check that `RATE_LIMIT_ENABLED=true` in your environment
2. Verify the user doesn't have exempt permissions
3. Check the configuration with `!ratelimit status`

### Users Complaining About Rate Limits
1. Check if the limits are too restrictive for your server
2. Consider adjusting `RATE_LIMIT_MAX_COMMANDS` or `RATE_LIMIT_WINDOW`
3. Verify the user doesn't need elevated permissions

### Need to Bypass Rate Limits Temporarily
Use `!ratelimit disable` to temporarily disable rate limiting, then `!ratelimit enable` to re-enable it.

## Best Practices

### Configuration Recommendations
- **Small servers (< 50 users)**: 2-3 commands per 10 seconds
- **Medium servers (50-200 users)**: 1-2 commands per 5 seconds  
- **Large servers (200+ users)**: 1 command per 5-10 seconds

### Permission Management
- Give trusted moderators `Manage Channels` permission to exempt them
- Use `Manage Guild` for senior moderators
- Reserve `Administrator` for server owners and co-owners

### Monitoring
- Regularly check `!ratelimit stats` for problematic users
- Monitor rate limit messages to adjust settings if needed
- Consider temporarily disabling during events or high-activity periods