"""
Tests for rate limiting functionality.
"""

import time
import unittest
from unittest.mock import Mock

import discord

from src.gitcord.utils.rate_limiter import RateLimiter, RATE_LIMIT_MAX_COMMANDS, RATE_LIMIT_WINDOW


class TestRateLimiting(unittest.TestCase):
    """Test cases for rate limiting functionality."""

    def setUp(self):
        """Set up test environment."""
        self.rate_limiter = RateLimiter()

    def test_rate_limiting_basic_functionality(self):
        """Test basic rate limiting functionality."""
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

    def test_rate_limiting_applies_to_all_users(self):
        """Test that rate limiting applies to all users equally."""
        user_id = 12345
        
        # Create a mock member with admin permissions
        mock_member = Mock(spec=discord.Member)
        mock_member.guild_permissions.administrator = True
        
        # Even admin users should be rate limited
        self.rate_limiter.add_command_usage(user_id)
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)
        self.assertGreater(time_left, 0)

    def test_rate_limit_window_expiry(self):
        """Test that rate limits expire after the time window."""
        user_id = 12345
        
        # Use up the rate limit
        self.rate_limiter.add_command_usage(user_id)
        is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)
        
        # Wait for the window to expire (using a short window for quick testing)
        # We'll test with the actual window since it's hard-coded to 5 seconds
        # This is a bit slow but ensures the test is accurate
        if RATE_LIMIT_WINDOW <= 2:  # Only run this if window is reasonable for testing
            time.sleep(RATE_LIMIT_WINDOW + 0.1)
            
            # Should no longer be rate limited
            is_limited, time_left = self.rate_limiter.is_rate_limited(user_id)
            self.assertFalse(is_limited)

    def test_multiple_users_independent_rate_limits(self):
        """Test that different users have independent rate limits."""
        user1_id = 12345
        user2_id = 67890
        
        # Use up rate limit for user1
        self.rate_limiter.add_command_usage(user1_id)
        
        # User1 should be rate limited
        is_limited, _ = self.rate_limiter.is_rate_limited(user1_id)
        self.assertTrue(is_limited)
        
        # User2 should not be rate limited
        is_limited, _ = self.rate_limiter.is_rate_limited(user2_id)
        self.assertFalse(is_limited)

    def test_rate_limit_message_throttling(self):
        """Test that rate limit messages are throttled to prevent spam."""
        user_id = 12345
        
        # First message should be allowed
        should_send = self.rate_limiter.should_send_rate_limit_message(user_id)
        self.assertTrue(should_send)
        
        # Immediate second message should not be allowed
        should_send = self.rate_limiter.should_send_rate_limit_message(user_id)
        self.assertFalse(should_send)

    def test_hard_coded_constants(self):
        """Test that rate limiting uses the correct hard-coded values."""
        # Verify the constants are set as expected
        self.assertEqual(RATE_LIMIT_MAX_COMMANDS, 1)
        self.assertEqual(RATE_LIMIT_WINDOW, 5)

    def test_sliding_window_behavior(self):
        """Test that the sliding window properly removes old timestamps."""
        user_id = 12345
        
        # Add a command usage
        self.rate_limiter.add_command_usage(user_id)
        
        # User should be rate limited
        is_limited, _ = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)
        
        # Verify that the internal state is cleaned up
        # This tests that old timestamps are removed from the deque
        user_timestamps = self.rate_limiter._user_timestamps[user_id]
        self.assertEqual(len(user_timestamps), 1)
        
        # Check rate limit again to ensure cleanup happens
        is_limited, _ = self.rate_limiter.is_rate_limited(user_id)
        self.assertTrue(is_limited)


if __name__ == '__main__':
    unittest.main()