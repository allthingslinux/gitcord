"""
Administrative commands cog for GitCord bot.
Contains admin-only utility commands.
"""

import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

import tempfile
import zipfile
import os
import shutil
import requests
from urllib.parse import urlparse, parse_qs

from .base_cog import BaseCog
from ..utils.helpers import create_embed, clean_webpage_text, parse_category_config_from_str, parse_channel_config_from_str
from ..cogs.channels import Channels
from discord.ui import View, Button
from ..views.base_views import DeleteExtraObjectsView


class Admin(BaseCog):
    """Administrative utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Admin cog."""
        super().__init__(bot)
        self.logger.info("Admin cog loaded")

    async def _fetch_url_content(self, url: str) -> str:
        """Fetch and clean content from a URL."""
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Fetch the webpage
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content and clean it
        text = soup.get_text()
        return clean_webpage_text(text)

    @commands.command(name="fetchurl")
    @commands.has_permissions(administrator=True)
    async def fetchurl_prefix(self, ctx: commands.Context, url: str) -> None:
        """Prefix command to fetch text content from a URL."""
        try:
            # Send initial response
            await ctx.send("🔄 Fetching content from URL...")

            # Fetch and process content
            text = await self._fetch_url_content(url)

            if not text.strip():
                await self.send_error(
                    ctx,
                    "❌ No Content Found",
                    "No readable text content was found on the provided URL.",
                )
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}",
            )

            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            await self.send_error(
                ctx, "❌ Fetch Error", f"Failed to fetch content from the URL: {str(e)}"
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Error in fetchurl command: %s", e)
            await self.send_error(
                ctx, "❌ Unexpected Error", f"An unexpected error occurred: {str(e)}"
            )

    @app_commands.command(
        name="fetchurl", description="Fetch and display text content from a URL"
    )
    @app_commands.describe(url="The URL to fetch text content from")
    @app_commands.checks.has_permissions(administrator=True)
    async def fetchurl(self, interaction: discord.Interaction, url: str) -> None:
        """Slash command to fetch text content from a URL."""
        await interaction.response.defer()

        try:
            # Fetch and process content
            text = await self._fetch_url_content(url)

            if not text.strip():
                await self.send_interaction_error(
                    interaction,
                    "❌ No Content Found",
                    "No readable text content was found on the provided URL.",
                )
                return

            # Create embed with the content
            embed = create_embed(
                title=f"📄 Content from {url}",
                description=f"```\n{text}\n```",
                color=discord.Color.blue(),
                footer=f"Fetched from {url}",
            )

            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException as e:
            await self.send_interaction_error(
                interaction,
                "❌ Fetch Error",
                f"Failed to fetch content from the URL: {str(e)}",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Error in fetchurl command: %s", e)
            await self.send_interaction_error(
                interaction,
                "❌ Unexpected Error",
                f"An unexpected error occurred: {str(e)}",
            )

    @app_commands.command(
        name="synccommands", description="Manually sync slash commands"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def synccommands(self, interaction: discord.Interaction) -> None:
        """Synchronize application commands for this guild."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                f"Synced {len(synced)} command(s).", ephemeral=True
            )
            self.logger.info(
                "Manually synced %d command(s) in guild: %s",
                len(synced),
                interaction.guild.name if interaction.guild else "N/A",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Failed to sync commands: %s", e)
            await interaction.followup.send(
                f"Failed to sync commands: {e}", ephemeral=True
            )

    @commands.command(name="synccommands")
    @commands.has_permissions(administrator=True)
    async def synccommands_prefix(self, ctx: commands.Context) -> None:
        """Prefix command to manually sync slash commands."""
        try:
            # Send initial response
            await ctx.send("🔄 Syncing slash commands...")

            synced = await self.bot.tree.sync(guild=ctx.guild)

            embed = create_embed(
                title="✅ Commands Synced",
                description=f"Successfully synced **{len(synced)}** command(s) for this guild.",
                color=discord.Color.green(),
            )

            await ctx.send(embed=embed)

            self.logger.info(
                "Manually synced %d command(s) in guild: %s via prefix command",
                len(synced),
                ctx.guild.name if ctx.guild else "N/A",
            )
        except (discord.DiscordException, OSError) as e:
            self.logger.error("Failed to sync commands via prefix command: %s", e)
            await self.send_error(
                ctx, "❌ Sync Failed", f"Failed to sync commands: {e}"
            )

    @commands.command(name="applytemplate")
    @commands.has_permissions(administrator=True)
    async def applytemplate_prefix(self, ctx: commands.Context, url: str, folder: str = None, branch: str = "main") -> None:
        self.logger.info(f"[applytemplate_prefix] User: {ctx.author}, URL: {url}, folder: {folder}, branch: {branch}")
        await ctx.send("🔄 Downloading and extracting template from GitHub...")
        try:
            temp_dir = self._download_and_extract_github(url, folder, branch)
            self.logger.info(f"[applytemplate_prefix] Extracted to: {temp_dir}")
            result_msgs = await self._apply_template_from_dir(ctx.guild, temp_dir, ctx=ctx)
            for msg in result_msgs:
                self.logger.info(f"[applytemplate_prefix] {msg}")
            await ctx.send("\n".join(result_msgs))
            shutil.rmtree(temp_dir)
            self.logger.info(f"[applytemplate_prefix] Cleaned up temp dir: {temp_dir}")
        except Exception as e:
            self.logger.error(f"[applytemplate_prefix] Error: {e}", exc_info=True)
            await self.send_error(ctx, "❌ Template Error", str(e))

    @app_commands.command(name="applytemplate", description="Apply a Gitcord template from a GitHub URL")
    @app_commands.describe(url="GitHub repo/folder URL", folder="Subfolder to use (optional)", branch="Branch/tag/commit (default: main)")
    @app_commands.checks.has_permissions(administrator=True)
    async def applytemplate(self, interaction: discord.Interaction, url: str, folder: str = None, branch: str = "main") -> None:
        self.logger.info(f"[applytemplate_slash] User: {interaction.user}, URL: {url}, folder: {folder}, branch: {branch}")
        await interaction.response.defer()
        try:
            temp_dir = self._download_and_extract_github(url, folder, branch)
            self.logger.info(f"[applytemplate_slash] Extracted to: {temp_dir}")
            result_msgs = await self._apply_template_from_dir(interaction.guild, temp_dir, interaction=interaction)
            for msg in result_msgs:
                self.logger.info(f"[applytemplate_slash] {msg}")
            await interaction.followup.send("\n".join(result_msgs))
            shutil.rmtree(temp_dir)
            self.logger.info(f"[applytemplate_slash] Cleaned up temp dir: {temp_dir}")
        except Exception as e:
            self.logger.error(f"[applytemplate_slash] Error: {e}", exc_info=True)
            await self.send_interaction_error(interaction, "❌ Template Error", str(e))

    def _download_and_extract_github(self, url: str, folder: str = None, branch: str = "main") -> str:
        """Download a GitHub repo/folder as zip, extract to temp dir, return path."""
        # Parse the URL
        parsed = urlparse(url)
        if "github.com" not in parsed.netloc:
            raise ValueError("Only GitHub URLs are supported.")
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL.")
        user, repo = path_parts[0], path_parts[1]
        # Determine zip URL
        zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip"
        # Download zip
        resp = requests.get(zip_url, stream=True, timeout=30)
        if resp.status_code != 200:
            raise ValueError(f"Failed to download zip from {zip_url} (status {resp.status_code})")
        temp_dir = tempfile.mkdtemp(prefix="gitcord-template-")
        zip_path = os.path.join(temp_dir, "repo.zip")
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        # Extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(zip_path)
        # Find the extracted folder
        extracted_root = None
        for name in os.listdir(temp_dir):
            if name.startswith(f"{repo}-"):
                extracted_root = os.path.join(temp_dir, name)
                break
        if not extracted_root:
            raise ValueError("Could not find extracted repo root.")
        # If a subfolder is specified, use it
        if folder:
            folder_path = os.path.join(extracted_root, folder)
            if not os.path.isdir(folder_path):
                raise ValueError(f"Subfolder '{folder}' not found in repo.")
            return folder_path
        return extracted_root

    async def _apply_template_from_dir(self, guild, template_dir, ctx=None, interaction=None):
        result_msgs = []
        template_category_names = set()
        template_channel_names = set()
        template_category_channel_pairs = set()
        # If you ever support uncategorized channels in the template, collect them here
        template_uncategorized_channel_names = set()
        for root, dirs, files in os.walk(template_dir):
            if "category.yaml" in files:
                cat_path = os.path.join(root, "category.yaml")
                self.logger.info(f"[apply_template_from_dir] Found category.yaml: {cat_path}")
                with open(cat_path, "r", encoding="utf-8") as f:
                    cat_yaml = f.read()
                try:
                    category_config = parse_category_config_from_str(cat_yaml)
                except Exception as e:
                    msg = f"❌ Failed to parse {cat_path}: {e}"
                    self.logger.error(f"[apply_template_from_dir] {msg}")
                    result_msgs.append(msg)
                    continue
                category_name = category_config["name"]
                template_category_names.add(category_name)
                for ch_name in category_config["channels"]:
                    template_channel_names.add(ch_name)
                    template_category_channel_pairs.add((category_name, ch_name))
                # Create or update the category
                existing_category = discord.utils.get(guild.categories, name=category_name)
                if existing_category:
                    category = existing_category
                    msg = f"ℹ️ Category '{category_name}' already exists. Will update channels."
                else:
                    category = await guild.create_category(name=category_name, position=category_config.get("position", 0))
                    msg = f"✅ Created category: {category_name}"
                self.logger.info(f"[apply_template_from_dir] {msg}")
                result_msgs.append(msg)
                # Create/update channels
                created, updated, skipped = 0, 0, 0
                for ch_name in category_config["channels"]:
                    ch_path = os.path.join(root, f"{ch_name}.yaml")
                    if not os.path.exists(ch_path):
                        msg = f"⚠️ Channel YAML not found: {ch_path}"
                        self.logger.warning(f"[apply_template_from_dir] {msg}")
                        result_msgs.append(msg)
                        skipped += 1
                        continue
                    with open(ch_path, "r", encoding="utf-8") as f:
                        ch_yaml = f.read()
                    try:
                        channel_config = parse_channel_config_from_str(ch_yaml)
                    except Exception as e:
                        msg = f"❌ Failed to parse {ch_path}: {e}"
                        self.logger.error(f"[apply_template_from_dir] {msg}")
                        result_msgs.append(msg)
                        skipped += 1
                        continue
                    # Check if channel exists
                    existing_channel = discord.utils.get(category.channels, name=channel_config["name"])
                    channel_type = channel_config["type"].lower()
                    if existing_channel:
                        # Update topic/nsfw/position if needed
                        update_kwargs = {}
                        if channel_type == "text" and hasattr(existing_channel, "topic") and existing_channel.topic != channel_config.get("topic", ""):
                            update_kwargs["topic"] = channel_config.get("topic", "")
                        if channel_type in ("text", "voice") and hasattr(existing_channel, "nsfw") and existing_channel.nsfw != channel_config.get("nsfw", False):
                            update_kwargs["nsfw"] = channel_config.get("nsfw", False)
                        if "position" in channel_config and hasattr(existing_channel, "position") and existing_channel.position != channel_config["position"]:
                            update_kwargs["position"] = channel_config["position"]
                        if update_kwargs:
                            await existing_channel.edit(**update_kwargs)
                            updated += 1
                            msg = f"🔄 Updated channel: {existing_channel.name} in {category_name}"
                        else:
                            skipped += 1
                            msg = f"⏭️ Skipped channel (no changes): {existing_channel.name} in {category_name}"
                        self.logger.info(f"[apply_template_from_dir] {msg}")
                        result_msgs.append(msg)
                    else:
                        # Create new channel
                        channel_kwargs = {"name": channel_config["name"], "category": category}
                        if "position" in channel_config:
                            channel_kwargs["position"] = channel_config["position"]
                        if channel_type == "text":
                            if "topic" in channel_config:
                                channel_kwargs["topic"] = channel_config["topic"]
                            if "nsfw" in channel_config:
                                channel_kwargs["nsfw"] = channel_config["nsfw"]
                            await guild.create_text_channel(**channel_kwargs)
                        elif channel_type == "voice":
                            await guild.create_voice_channel(**channel_kwargs)
                        else:
                            msg = f"❌ Unknown channel type: {channel_type} for {channel_config['name']}"
                            self.logger.error(f"[apply_template_from_dir] {msg}")
                            result_msgs.append(msg)
                            skipped += 1
                            continue
                        created += 1
                        msg = f"✅ Created channel: {channel_config['name']} in {category_name}"
                        self.logger.info(f"[apply_template_from_dir] {msg}")
                        result_msgs.append(msg)
                # After all channels processed, check for extra channels in this category
                template_channel_names = set(category_config["channels"])
                extra_channels = [ch for ch in category.channels if ch.name not in template_channel_names]
                if extra_channels:
                    msg = f"⚠️ Extra channels not in template for category '{category_name}': {', '.join(ch.name for ch in extra_channels)}"
                    self.logger.warning(f"[apply_template_from_dir] {msg}")
                    result_msgs.append(msg)
                    view = DeleteExtraObjectsView(extra_channels, object_type_label='channel')
                    if interaction:
                        await interaction.followup.send(msg, view=view)
                    elif ctx:
                        await ctx.send(msg, view=view)
                summary = f"**{category_name}**: {created} created, {updated} updated, {skipped} skipped"
                result_msgs.append(summary)
        # After all categories processed, check for extra categories
        existing_category_names = set(cat.name for cat in guild.categories)
        extra_categories = [cat for cat in guild.categories if cat.name not in template_category_names]
        if extra_categories:
            msg = f"⚠️ Extra categories not in template: {', '.join(cat.name for cat in extra_categories)}"
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(extra_categories, object_type_label='category')
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        # After all categories processed, check for orphan channels
        orphan_channels = []
        for ch in guild.channels:
            if getattr(ch, 'category', None) is None and isinstance(ch, (discord.TextChannel, discord.VoiceChannel)):
                # If template does not support uncategorized channels, all orphans are extra
                # If template_uncategorized_channel_names is empty, all orphans are extra
                if not template_uncategorized_channel_names or ch.name not in template_uncategorized_channel_names:
                    orphan_channels.append(ch)
        if orphan_channels:
            msg = f"⚠️ Uncategorized channels not in template: {', '.join(ch.name for ch in orphan_channels)}"
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(orphan_channels, object_type_label='channel')
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        if not result_msgs:
            msg = "⚠️ No categories found in template."
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
        return result_msgs


async def setup(bot: commands.Bot) -> None:
    """Set up the Admin cog."""
    await bot.add_cog(Admin(bot))
