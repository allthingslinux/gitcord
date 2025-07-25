"""
Tests for rate limiting functionality.
"""

import time
import unittest
from unittest.mock import Mock, patch

import discord

from src.gitcord.config import Config
from src.gitcord.utils.rate_limiter import RateLimiter


class TestRateLimiting(unittest.TestCase):
    """Test cases for rate limiting functionality."""

    def setUp(self):
        """Set up test environment."""
        self.rate_limiter = RateLimiter()
        # Create a mock config with test values
        self.mock_config = Mock()
        self.mock_config.rate_limit_enabled = True
        self.mock_config.rate_limit_max_commands = 1
        self.mock_config.rate_limit_window = 5

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_rate_limiting_basic_functionality(self, mock_config):
        """Test basic rate limiting functionality."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_max_commands = 1
        mock_config.rate_limit_window = 5
        
        user_id = 12345
        
        # First command should be allowed
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertFalse(is_limited)
        self.assertEqual(time_left, 0.0)
        
        # Record the command usage
        self.rate_limiter.add_command_usage(user_id)
        
        # Second command should be rate limited
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)
        self.assertGreater(time_left, 0)

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_exempt_user_not_rate_limited(self, mock_config):
        """Test that exempt users (admins/mods) are not rate limited."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_max_commands = 1
        mock_config.rate_limit_window = 5
        
        user_id = 12345
        
        # Create a mock member with admin permissions
        mock_member = Mock(spec=discord.Member)
        mock_member.guild_permissions.administrator = True
        
        # Admin user should not be rate limited even after multiple commands
        for _ in range(5):
            is_limited, time_left = self.rate_limiter.is_rate_limited(user_id, mock_member)
            self.assertFalse(is_limited)
            self.assertEqual(time_left, 0.0)
            self.rate_limiter.add_command_usage(user_id, mock_member)

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_rate_limiting_disabled_globally(self, mock_config):
        """Test that rate limiting can be disabled globally."""
        mock_config.rate_limit_enabled = False
        mock_config.rate_limit_max_commands = 1
        mock_config.rate_limit_window = 5
        
        user_id = 12345
        
        # Even after multiple commands, user should not be rate limited
        for _ in range(5):
            is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
            self.assertFalse(is_limited)
            self.assertEqual(time_left, 0.0)
            self.rate_limiter.add_command_usage(user_id)

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_rate_limit_window_expiry(self, mock_config):
        """Test that rate limits expire after the time window."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_max_commands = 1
        mock_config.rate_limit_window = 1  # 1 second window for quick testing
        
        user_id = 12345
        
        # Use up the rate limit
        self.rate_limiter.add_command_usage(user_id)
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)
        
        # Wait for the window to expire
        time.sleep(1.1)
        
        # Should no longer be rate limited
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertFalse(is_limited)

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_get_user_stats(self, mock_config):
        """Test getting user rate limit statistics."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_max_commands = 3
        mock_config.rate_limit_window = 10
        
        user_id = 12345
        
        # Initially should have 0 commands used
        stats = self.rate_limiter.get_user_stats(user_id)
        self.assertEqual(stats['commands_used'], 0)
        self.assertEqual(stats['max_commands'], 3)
        self.assertEqual(stats['window_seconds'], 10)
        self.assertFalse(stats['is_limited'])
        
        # Add some command usage
        self.rate_limiter.add_command_usage(user_id)
        self.rate_limiter.add_command_usage(user_id)
        
        stats = self.rate_limiter.get_user_stats(user_id)
        self.assertEqual(stats['commands_used'], 2)
        self.assertFalse(stats['is_limited'])
        
        # Hit the limit
        self.rate_limiter.add_command_usage(user_id)
        
        stats = self.rate_limiter.get_user_stats(user_id)
        self.assertEqual(stats['commands_used'], 3)
        self.assertTrue(stats['is_limited'])

    @patch('src.gitcord.utils.rate_limiter.config')
    def test_manage_channels_permission_exempt(self, mock_config):
        """Test that users with manage_channels permission are exempt."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_max_commands = 1
        mock_config.rate_limit_window = 5
        
        user_id = 12345
        
        # Create a mock member with manage_channels permissions
        mock_member = Mock(spec=discord.Member)
        mock_member.guild_permissions.administrator = False
        mock_member.guild_permissions.manage_guild = False
        mock_member.guild_permissions.manage_channels = True
        
        # User should not be rate limited
        for _ in range(5):
            is_limited, time_left = self.rate_limiter.is_rate_limited(user_id, mock_member)
            self.assertFalse(is_limited)
            self.rate_limiter.add_command_usage(user_id, mock_member)


if __name__ == '__main__':
    unittest.main()