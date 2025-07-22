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
        self.result: bool | None = None

        # Add confirm and cancel buttons
        confirm_button: Button = Button(
            label="✅ Confirm", style=discord.ButtonStyle.success, custom_id="confirm"
        )
        confirm_button.callback = self.confirm_callback

        cancel_button: Button = Button(
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
            description=self.description,
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def cancel_callback(self, interaction: discord.Interaction):
        """Handle cancel button click."""
        self.result = False
        embed = create_embed(
            title="❌ Cancelled",
            description="Action was cancelled."
        )
        await interaction.response.edit_message(embed=embed, view=None)


class ErrorView(BaseView):
    """View for displaying errors with a close button."""

    def __init__(self, title: str, description: str, timeout=30):
        super().__init__(timeout=timeout)
        self.title = title
        self.description = description

        close_button: Button = Button(
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
        loading_button: Button = Button(
            label="⏳ " + message,
            style=discord.ButtonStyle.secondary,
            disabled=True,
            custom_id="loading",
        )
        self.add_item(loading_button)


class DeleteExtraObjectsView(View):
    """
    Generic view for confirming deletion of extra Discord objects (channels, categories, etc.).
    Objects must have .name and .delete().
    """

    def __init__(self, extra_objects, object_type_label, timeout=60):
        super().__init__(timeout=timeout)
        self.extra_objects = extra_objects
        self.object_type_label = object_type_label
        delete_button = Button(
            label=f"🗑️ Delete Extra {object_type_label.title()}s",
            style=discord.ButtonStyle.danger,
            custom_id=f"delete_extra_{object_type_label}s",
        )
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

    async def delete_callback(self, interaction: discord.Interaction):
        # Check permissions (manage_channels for channels, manage_channels for categories)
        if not interaction.user.guild_permissions.manage_channels:  # type: ignore
            from ..utils.helpers import create_embed

            embed = create_embed(
                title="❌ Permission Denied",
                description=f"You need the 'Manage Channels' permission to delete {self.object_type_label}s.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        # Create confirmation embed
        object_list = "\n".join(
            [
                f"• {getattr(obj, 'mention', '#' + obj.name)}"
                for obj in self.extra_objects
            ]
        )
        from ..utils.helpers import create_embed

        embed = create_embed(
            title="⚠️ Confirm Deletion",
            description=(
                f"Are you sure you want to delete the following {self.object_type_label}s?\n\n{object_list}\n\n**This action is irreversible!**"
            ),
            color=discord.Color.orange(),
        )
        confirm_view = ConfirmDeleteObjectsView(
            self.extra_objects, self.object_type_label
        )
        await interaction.response.send_message(
            embed=embed, view=confirm_view, ephemeral=True
        )


class ConfirmDeleteObjectsView(View):
    """
    View for final confirmation of object deletion.
    Objects must have .name and .delete().
    """

    def __init__(self, extra_objects, object_type_label, timeout=60):
        super().__init__(timeout=timeout)
        self.extra_objects = extra_objects
        self.object_type_label = object_type_label
        confirm_button = Button(
            label="✅ Yes, Delete All",
            style=discord.ButtonStyle.danger,
            custom_id="confirm_delete",
        )
        confirm_button.callback = self.confirm_callback
        cancel_button = Button(
            label="❌ Cancel",
            style=discord.ButtonStyle.secondary,
            custom_id="cancel_delete",
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(confirm_button)
        self.add_item(cancel_button)

    async def confirm_callback(self, interaction: discord.Interaction):
        deleted = []
        failed = []
        for obj in self.extra_objects:
            try:
                await obj.delete()
                deleted.append(obj.name)
            except Exception:
                failed.append(obj.name)
        from ..utils.helpers import create_embed

        if deleted:
            embed = create_embed(
                title=f"✅ {self.object_type_label.title()}s Deleted",
                description=f"Successfully deleted {len(deleted)} {self.object_type_label}s.",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Deleted",
                value="\n".join([f"• {name}" for name in deleted]),
                inline=False,
            )
            if failed:
                embed.add_field(
                    name="Failed",
                    value="\n".join([f"• {name}" for name in failed]),
                    inline=False,
                )
        else:
            embed = create_embed(
                title="❌ Deletion Failed",
                description="Failed to delete any objects. Please check permissions and try again.",
                color=discord.Color.red(),
            )
        await interaction.response.edit_message(embed=embed, view=None)

    async def cancel_callback(self, interaction: discord.Interaction):
        from ..utils.helpers import create_embed

        embed = create_embed(
            title="❌ Deletion Cancelled",
            description=f"{self.object_type_label.title()} deletion was cancelled."
        )
        await interaction.response.edit_message(embed=embed, view=None)
