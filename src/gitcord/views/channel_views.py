"""
Channel management UI components for GitCord bot.
"""

import discord
from discord.ui import Button, View

from ..utils.helpers import create_embed
from ..utils.logger import main_logger as logger


class DeleteExtraChannelsView(View):
    """View for confirming deletion of extra channels."""

    def __init__(self, extra_channels, category_name, timeout=60):
        super().__init__(timeout=timeout)
        self.extra_channels = extra_channels
        self.category_name = category_name

        # Add delete button
        delete_button = Button(
            label="🗑️ Delete Extra Channels",
            style=discord.ButtonStyle.danger,
            custom_id="delete_extra_channels",
        )
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

    async def delete_callback(self, interaction: discord.Interaction):
        """Handle delete button click."""
        # Check if user has manage channels permission
        if not interaction.user.guild_permissions.manage_channels:  # type: ignore
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to delete channels.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create confirmation embed
        channel_list = "\n".join(
            [f"• {channel.mention}" for channel in self.extra_channels]
        )
        embed = create_embed(
            title="⚠️ Confirm Deletion",
            description=(
                f"Are you sure you want to delete the following channels from "
                f"**{self.category_name}**?\n\n{channel_list}\n\n**This action is irreversible!**"
            ),
            color=discord.Color.orange(),
        )

        # Create confirmation view
        confirm_view = ConfirmDeleteView(self.extra_channels, self.category_name)
        await interaction.response.send_message(
            embed=embed, view=confirm_view, ephemeral=True
        )


class ConfirmDeleteView(View):
    """View for final confirmation of channel deletion."""

    def __init__(self, extra_channels, category_name, timeout=60):
        super().__init__(timeout=timeout)
        self.extra_channels = extra_channels
        self.category_name = category_name

        # Add confirm and cancel buttons
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
        """Handle confirm button click."""
        deleted_channels = []
        failed_channels = []

        # Delete each channel
        for channel in self.extra_channels:
            try:
                channel_name = channel.name
                await channel.delete()
                deleted_channels.append(channel_name)
                logger.info(
                    "Deleted extra channel '%s' from category '%s'",
                    channel_name,
                    self.category_name,
                )
            except (discord.Forbidden, discord.HTTPException, OSError) as e:
                failed_channels.append(channel.name)
                logger.error("Failed to delete channel '%s': %s", channel.name, e)

        # Create result embed
        if deleted_channels:
            embed = create_embed(
                title="✅ Channels Deleted",
                description=(
                    f"Successfully deleted {len(deleted_channels)} extra channels "
                    f"from **{self.category_name}**"
                ),
                color=discord.Color.green(),
            )

            if deleted_channels:
                deleted_list = "\n".join([f"• #{name}" for name in deleted_channels])
                embed.add_field(
                    name="Deleted Channels", value=deleted_list, inline=False
                )

            if failed_channels:
                failed_list = "\n".join([f"• #{name}" for name in failed_channels])
                embed.add_field(
                    name="Failed to Delete", value=failed_list, inline=False
                )
        else:
            embed = create_embed(
                title="❌ Deletion Failed",
                description=(
                    "Failed to delete any channels. Please check permissions and try again."
                ),
                color=discord.Color.red(),
            )

        await interaction.response.edit_message(embed=embed, view=None)

    async def cancel_callback(self, interaction: discord.Interaction):
        """Handle cancel button click."""
        embed = create_embed(
            title="❌ Deletion Cancelled",
            description="Channel deletion was cancelled."
        )
        await interaction.response.edit_message(embed=embed, view=None)
