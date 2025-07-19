"""
Base UI components and utilities for GitCord bot views.
"""

import discord
from discord.ui import Button, View

from ..utils.helpers import create_embed


class BaseView(View):
    """Base view class with common functionality."""

    def __init__(self, timeout=60):
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        """Handle view timeout."""
        # Disable all buttons when view times out
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

    def disable_all_buttons(self):
        """Disable all buttons in the view."""
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True


class ConfirmationView(BaseView):
    """Base confirmation view with yes/no buttons."""

    def __init__(self, title: str, description: str, timeout=60):
        super().__init__(timeout=timeout)
        self.title = title
        self.description = description
        self.result = None

        # Add confirm and cancel buttons
        confirm_button = Button(
            label="✅ Confirm", style=discord.ButtonStyle.success, custom_id="confirm"
        )
        confirm_button.callback = self.confirm_callback

        cancel_button = Button(
            label="❌ Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel"
        )
        cancel_button.callback = self.cancel_callback

        self.add_item(confirm_button)
        self.add_item(cancel_button)

    async def confirm_callback(self, interaction: discord.Interaction):
        """Handle confirm button click."""
        self.result = True
        embed = create_embed(
            title="✅ Confirmed",
            description="Action confirmed successfully.",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def cancel_callback(self, interaction: discord.Interaction):
        """Handle cancel button click."""
        self.result = False
        embed = create_embed(
            title="❌ Cancelled",
            description="Action was cancelled.",
            color=discord.Color.blue(),
        )
        await interaction.response.edit_message(embed=embed, view=None)


class ErrorView(BaseView):
    """View for displaying errors with a close button."""

    def __init__(self, title: str, description: str, timeout=30):
        super().__init__(timeout=timeout)

        close_button = Button(
            label="❌ Close", style=discord.ButtonStyle.secondary, custom_id="close"
        )
        close_button.callback = self.close_callback
        self.add_item(close_button)

    async def close_callback(self, interaction: discord.Interaction):
        """Handle close button click."""
        if interaction.message:
            await interaction.message.delete()


class LoadingView(BaseView):
    """View for showing loading state."""

    def __init__(self, message: str = "Loading...", timeout=30):
        super().__init__(timeout=timeout)

        # Create a disabled button to show loading state
        loading_button = Button(
            label="⏳ " + message,
            style=discord.ButtonStyle.secondary,
            disabled=True,
            custom_id="loading",
        )
        self.add_item(loading_button)
