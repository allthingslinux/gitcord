"""
Administrative commands cog for GitCord bot.
Contains admin-only utility commands.
"""

import discord
from discord import app_commands
from discord.ext import commands

import tempfile
import zipfile
import os
import shutil
from urllib.parse import urlparse
import re
import requests
import subprocess

from .base_cog import BaseCog
from ..utils.helpers import (
    create_embed,
    clean_webpage_text,
    parse_category_config_from_str,
    parse_channel_config_from_str,
    create_error_embed,
    create_success_embed,
)
from ..views.base_views import DeleteExtraObjectsView
from ..utils import template_metadata
from ..utils.rate_limiter import rate_limit
from ..constants.paths import get_template_repo_dir


class Admin(BaseCog):
    """Administrative utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Admin cog."""
        super().__init__(bot)
        self.logger.info("Admin cog loaded")

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

    @rate_limit()
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

    def _convert_to_git_style_diff(self, result_msgs: list) -> str:
        """Convert verbose template messages to git-style diff format."""
        diff_lines = []
        
        for msg in result_msgs:
            # Skip summary lines and info messages
            if "**" in msg or msg.startswith("ℹ️") or "already exists" in msg:
                continue
                
            # Parse different message types
            if "🔄 Updated channel:" in msg or "🔄 Updated category:" in msg:
                # Extract name: "🔄 Updated channel: moderator-only in Boilerplate" -> "M  moderator-only"
                parts = msg.split(": ", 1)[1].split(" in ")
                name = parts[0] if parts else "unknown"
                diff_lines.append(f"M  {name}")
            elif "Created channel:" in msg or "Created category:" in msg:
                # Extract name: "Created channel: new-channel in Category" -> "A  new-channel"
                parts = msg.split(": ", 1)[1].split(" in ")
                name = parts[0] if parts else "unknown"
                diff_lines.append(f"A  {name}")
            elif "Deleted channel:" in msg or "Deleted category:" in msg:
                # Extract name for deletions
                parts = msg.split(": ", 1)[1].split(" in ")
                name = parts[0] if parts else "unknown"
                diff_lines.append(f"D  {name}")
            # Skip "Skipped" messages as they indicate no changes
            
        return "\n".join(diff_lines) if diff_lines else "No changes"

    @rate_limit()
    @commands.command(name="git")
    @commands.has_permissions(administrator=True)
    async def git_command(self, ctx: commands.Context, *args):
        """Handle !git clone <url> [-b branch], !git pull, and warn on others."""
        if not args:
            embed = create_error_embed(
                "❌ Invalid Usage", 
                "Usage: `!git clone <url> [-b branch]` or `!git pull`"
            )
            await ctx.send(embed=embed)
            return
        
        cmd = args[0]
        guild_id = ctx.guild.id
        repo_dir = get_template_repo_dir(guild_id)
        
        if cmd == "clone":
            if len(args) < 2:
                embed = create_error_embed(
                    "❌ Missing Repository URL",
                    "Usage: `!git clone <url> [-b branch]`"
                )
                await ctx.send(embed=embed)
                return
            
            url = args[1]
            branch = "main"
            if len(args) >= 4 and args[2] == "-b":
                branch = args[3]
            
            # Remove existing repo if present
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            os.makedirs(repo_dir, exist_ok=True)
            
            try:
                result = subprocess.run([
                    "git", "clone", "-b", branch, url, repo_dir
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    error_embed = create_error_embed(
                        "❌ Git Clone Failed",
                        f"```\n{result.stderr}\n```"
                    )
                    await ctx.send(embed=error_embed)
                    return
                
                # Save metadata
                template_metadata.save_metadata(guild_id, {
                    "url": url,
                    "branch": branch,
                    "local_path": repo_dir
                })
                
                # Always show success
                success_embed = create_success_embed(
                    "✅ Repository Cloned",
                    f"Template repository cloned successfully\n`{url}` (branch: `{branch}`)"
                )
                await ctx.send(embed=success_embed)
                
                # Show warnings if any
                if result.stderr.strip():
                    warning_embed = create_embed(
                        title="⚠️ Clone Warnings",
                        description=f"```\n{result.stderr}\n```",
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=warning_embed)
                    
            except subprocess.TimeoutExpired:
                timeout_embed = create_error_embed(
                    "⏰ Clone Timeout",
                    "Git clone operation timed out after 60 seconds."
                )
                await ctx.send(embed=timeout_embed)
            except Exception as e:
                error_embed = create_error_embed(
                    "❌ Clone Error",
                    f"```\n{str(e)}\n```"
                )
                await ctx.send(embed=error_embed)
                
        elif cmd == "pull":
            meta = template_metadata.load_metadata(guild_id)
            if not meta or not os.path.exists(meta.get("local_path", "")):
                embed = create_error_embed(
                    "❌ No Template Repository",
                    "Run `!git clone <url>` first to set up a template repository."
                )
                await ctx.send(embed=embed)
                return
            
            try:
                result = subprocess.run([
                    "git", "pull"
                ], cwd=meta["local_path"], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    error_embed = create_error_embed(
                        "❌ Git Pull Failed",
                        f"```\n{result.stderr}\n```"
                    )
                    await ctx.send(embed=error_embed)
                    return
                
                # Always show basic success
                git_output = result.stdout.strip()
                if git_output and git_output != "Already up to date.":
                    # Show changes
                    success_embed = create_success_embed(
                        "✅ Repository Updated",
                        f"```\n{git_output}\n```"
                    )
                else:
                    # Show "already up to date"
                    success_embed = create_success_embed(
                        "✅ Repository Up To Date",
                        "No changes found in remote repository"
                    )
                await ctx.send(embed=success_embed)
                
                # Show git warnings if any
                if result.stderr.strip():
                    warning_embed = create_embed(
                        title="⚠️ Git Warnings",
                        description=f"```\n{result.stderr}\n```",
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=warning_embed)
                
                try:
                    # Always apply template to ensure Discord matches the template
                    # (Even if git says "up to date", Discord might not match the template)
                    result_msgs = await self._apply_template_from_dir(ctx.guild, meta["local_path"], ctx=ctx)
                    
                    # Convert to git-style diff
                    if result_msgs:
                        # Check for warnings/errors first
                        warnings = [msg for msg in result_msgs if "warning" in msg.lower() or "error" in msg.lower() or "failed" in msg.lower()]
                        
                        # Show warnings if any
                        if warnings:
                            template_warning_embed = create_embed(
                                title="⚠️ Template Warnings",
                                description=f"```\n{chr(10).join(warnings)}\n```",
                                color=discord.Color.orange()
                            )
                            await ctx.send(embed=template_warning_embed)
                        
                        # Convert to git-style diff
                        git_diff = self._convert_to_git_style_diff(result_msgs)
                        
                        if git_diff and git_diff != "No changes":
                            template_changes_embed = create_success_embed(
                                "✅ Template Applied",
                                f"```\n{git_diff}\n```"
                            )
                            await ctx.send(embed=template_changes_embed)
                        else:
                            # No changes
                            template_success_embed = create_success_embed(
                                "✅ Template Applied",
                                "No changes needed"
                            )
                            await ctx.send(embed=template_success_embed)
                    else:
                        # No template results
                        template_success_embed = create_success_embed(
                            "✅ Template Applied",
                            "No output from template processing"
                        )
                        await ctx.send(embed=template_success_embed)
                        
                except Exception as e:
                    self.logger.error(f"[git pull apply] Error: {e}", exc_info=True)
                    error_embed = create_error_embed(
                        "❌ Template Application Failed",
                        f"```\n{str(e)}\n```"
                    )
                    await ctx.send(embed=error_embed)
                    
            except subprocess.TimeoutExpired:
                timeout_embed = create_error_embed(
                    "⏰ Pull Timeout",
                    "Git pull operation timed out after 60 seconds."
                )
                await ctx.send(embed=timeout_embed)
            except Exception as e:
                error_embed = create_error_embed(
                    "❌ Pull Error",
                    f"```\n{str(e)}\n```"
                )
                await ctx.send(embed=error_embed)
        else:
            embed = create_error_embed(
                "⚠️ Unsupported Git Command",
                f"Only `git clone` and `git pull` are supported. You tried: `!git {cmd}`"
            )
            await ctx.send(embed=embed)

    # Patch applytemplate to use local repo if present
    def _get_template_dir(self, folder=None, guild_id=None):
        meta = template_metadata.load_metadata(guild_id)
        if meta and os.path.exists(meta.get("local_path", "")):
            repo_root = meta["local_path"]
            if folder:
                folder_path = os.path.join(repo_root, folder)
                if os.path.isdir(folder_path):
                    return folder_path
                else:
                    raise ValueError(f"Subfolder '{folder}' not found in local template repo.")
            return repo_root
        return None

    @rate_limit()
    @commands.command(name="applytemplate")
    @commands.has_permissions(administrator=True)
    async def applytemplate_prefix(self, ctx: commands.Context, url: str = None, folder: str = None, branch: str = "main"):
        await ctx.send("⚠️ The !applytemplate command is deprecated. Please use !git clone and !git pull instead.")
        template_dir = None
        guild_id = ctx.guild.id
        if url is None:
            template_dir = self._get_template_dir(folder, guild_id)
            if not template_dir:
                await ctx.send("❌ No local template repo found for this server. Use !git clone or provide a URL.")
                return
        if template_dir:
            await ctx.send("🔄 Applying template from local repo...")
            try:
                result_msgs = await self._apply_template_from_dir(ctx.guild, template_dir, ctx=ctx)
                for msg in result_msgs:
                    self.logger.info(f"[applytemplate_prefix] {msg}")
                await ctx.send("\n".join(result_msgs))
            except Exception as e:
                self.logger.error(f"[applytemplate_prefix] Error: {e}", exc_info=True)
                await self.send_error(ctx, "❌ Template Error", str(e))
            return
        # Fallback to old logic if URL is provided
        if not re.match(r"^https?://github\.com/[^/]+/[^/]+", url):
            await ctx.send("❌ Only direct github.com repository URLs are supported.")
            return
        self.logger.info(
            f"[applytemplate_prefix] User: {ctx.author}, URL: {url}, folder: {folder}, branch: {branch}"
        )
        await ctx.send("🔄 Downloading and extracting template from GitHub...")
        try:
            temp_dir = self._download_and_extract_github(url, folder, branch)
            self.logger.info(f"[applytemplate_prefix] Extracted to: {temp_dir}")
            result_msgs = await self._apply_template_from_dir(
                ctx.guild, temp_dir, ctx=ctx
            )
            for msg in result_msgs:
                self.logger.info(f"[applytemplate_prefix] {msg}")
            await ctx.send("\n".join(result_msgs))
            shutil.rmtree(temp_dir)
            self.logger.info(f"[applytemplate_prefix] Cleaned up temp dir: {temp_dir}")
        except Exception as e:
            self.logger.error(f"[applytemplate_prefix] Error: {e}", exc_info=True)
            await self.send_error(ctx, "❌ Template Error", str(e))

    @app_commands.command(
        name="applytemplate", description="Apply a Gitcord template from a GitHub URL (deprecated, use !git pull)"
    )
    @app_commands.describe(
        url="GitHub repo/folder URL (optional if using !git clone)",
        folder="Subfolder to use (optional)",
        branch="Branch/tag/commit (default: main)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def applytemplate(
        self,
        interaction: discord.Interaction,
        url: str = None,
        folder: str = None,
        branch: str = "main",
    ) -> None:
        await interaction.response.send_message("⚠️ The /applytemplate command is deprecated. Please use !git clone and !git pull instead.", ephemeral=True)
        template_dir = None
        guild_id = interaction.guild.id
        if url is None:
            template_dir = self._get_template_dir(folder, guild_id)
            if not template_dir:
                await interaction.response.send_message("❌ No local template repo found for this server. Use !git clone or provide a URL.", ephemeral=True)
                return
        if template_dir:
            await interaction.response.defer()
            try:
                result_msgs = await self._apply_template_from_dir(interaction.guild, template_dir, interaction=interaction)
                for msg in result_msgs:
                    self.logger.info(f"[applytemplate_slash] {msg}")
                await interaction.followup.send("\n".join(result_msgs))
            except Exception as e:
                self.logger.error(f"[applytemplate_slash] Error: {e}", exc_info=True)
                await self.send_interaction_error(interaction, "❌ Template Error", str(e))
            return
        # Fallback to old logic if URL is provided
        if not re.match(r"^https?://github\.com/[^/]+/[^/]+", url):
            await interaction.response.send_message("❌ Only direct github.com repository URLs are supported.", ephemeral=True)
            return
        self.logger.info(
            f"[applytemplate_slash] User: {interaction.user}, URL: {url}, folder: {folder}, branch: {branch}"
        )
        await interaction.response.defer()
        try:
            temp_dir = self._download_and_extract_github(url, folder, branch)
            self.logger.info(f"[applytemplate_slash] Extracted to: {temp_dir}")
            result_msgs = await self._apply_template_from_dir(
                interaction.guild, temp_dir, interaction=interaction
            )
            for msg in result_msgs:
                self.logger.info(f"[applytemplate_slash] {msg}")
            await interaction.followup.send("\n".join(result_msgs))
            shutil.rmtree(temp_dir)
            self.logger.info(f"[applytemplate_slash] Cleaned up temp dir: {temp_dir}")
        except Exception as e:
            self.logger.error(f"[applytemplate_slash] Error: {e}", exc_info=True)
            await self.send_interaction_error(interaction, "❌ Template Error", str(e))

    def _download_and_extract_github(
        self, url: str, folder: str = None, branch: str = "main"
    ) -> str:
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
            raise ValueError(
                f"Failed to download zip from {zip_url} (status {resp.status_code})"
            )
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

    async def _apply_template_from_dir(
        self, guild, template_dir, ctx=None, interaction=None
    ):
        """Apply template from directory - now looks for monolithic template.yaml first, falls back to legacy format."""
        # Try monolithic template format first
        template_path = os.path.join(template_dir, "template.yaml")
        if os.path.exists(template_path):
            return await self._apply_monolithic_template(guild, template_path, ctx, interaction)
        
        # Fall back to legacy directory-based format
        result_msgs = []
        template_category_names = set()
        template_channel_names = set()
        template_category_channel_pairs = set()
        # If you ever support uncategorized channels in the template, collect them here
        template_uncategorized_channel_names = set()
        
        # First, collect all categories to determine their order
        category_paths = []
        for root, dirs, files in os.walk(template_dir):
            if "category.yaml" in files:
                category_paths.append(root)
        
        # Sort to ensure consistent ordering (alphabetical by directory name)
        category_paths.sort()
        
        for category_index, root in enumerate(category_paths):
            cat_path = os.path.join(root, "category.yaml")
            self.logger.info(
                f"[apply_template_from_dir] Found category.yaml: {cat_path}"
            )
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
            existing_category = discord.utils.get(
                guild.categories, name=category_name
            )
            if existing_category:
                category = existing_category
                msg = f"ℹ️ Category '{category_name}' already exists. Will update channels."
                
                # Check if category is in correct relative order (smart positioning)
                guild_categories = sorted(guild.categories, key=lambda cat: cat.position)
                current_relative_index = guild_categories.index(category)
                
                if current_relative_index != category_index:
                    try:
                        await category.edit(position=category_index)
                        msg += f" Moved to position {category_index}."
                    except (discord.Forbidden, discord.HTTPException) as e:
                        self.logger.warning(f"Failed to update category position: {e}")
            else:
                category = await guild.create_category(
                    name=category_name, 
                    position=category_index
                )
                msg = f"✅ Created category: {category_name} at position {category_index}"
            self.logger.info(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
            # Create/update channels
            created, updated, skipped = 0, 0, 0
            for channel_index, ch_name in enumerate(category_config["channels"]):
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
                existing_channel = discord.utils.get(
                    category.channels, name=channel_config["name"]
                )
                channel_type = channel_config["type"].lower()
                if existing_channel:
                    # Update topic/nsfw and position if needed
                    update_kwargs = {}
                    if (
                        channel_type == "text"
                        and hasattr(existing_channel, "topic")
                        and existing_channel.topic
                        != channel_config.get("topic", "")
                    ):
                        update_kwargs["topic"] = channel_config.get("topic", "")
                    if (
                        channel_type in ("text", "voice")
                        and hasattr(existing_channel, "nsfw")
                        and existing_channel.nsfw
                        != channel_config.get("nsfw", False)
                    ):
                        update_kwargs["nsfw"] = channel_config.get("nsfw", False)
                    
                    # Check if channel is in correct relative order (smart positioning)
                    if hasattr(existing_channel, "position"):
                        # Get all channels in category sorted by position
                        category_channels = sorted(category.channels, key=lambda ch: ch.position)
                        current_relative_index = category_channels.index(existing_channel)
                        
                        # Only move if the channel is not at the correct relative position
                        if current_relative_index != channel_index:
                            update_kwargs["position"] = channel_index
                    
                    if update_kwargs:
                        await existing_channel.edit(**update_kwargs)
                        updated += 1
                        position_msg = f" (position {channel_index})" if "position" in update_kwargs else ""
                        msg = f"🔄 Updated channel: {existing_channel.name} in {category_name}{position_msg}"
                    else:
                        skipped += 1
                        msg = f"⏭️ Skipped channel (no changes): {existing_channel.name} in {category_name}"
                    self.logger.info(f"[apply_template_from_dir] {msg}")
                    result_msgs.append(msg)
                else:
                    # Create new channel with proper position
                    channel_kwargs = {
                        "name": channel_config["name"],
                        "category": category,
                        "position": channel_index,
                    }
                    if channel_type == "text":
                        if "topic" in channel_config:
                            channel_kwargs["topic"] = channel_config["topic"]
                        if "nsfw" in channel_config:
                            channel_kwargs["nsfw"] = channel_config["nsfw"]
                        await guild.create_text_channel(**channel_kwargs)
                    elif channel_type == "voice":
                        # Voice channels don't support topic
                        if "topic" in channel_kwargs:
                            del channel_kwargs["topic"]
                        if "nsfw" in channel_config:
                            channel_kwargs["nsfw"] = channel_config["nsfw"]
                        await guild.create_voice_channel(**channel_kwargs)
                    else:
                        msg = f"❌ Unknown channel type: {channel_type} for {channel_config['name']}"
                        self.logger.error(f"[apply_template_from_dir] {msg}")
                        result_msgs.append(msg)
                        skipped += 1
                        continue
                    created += 1
                    msg = f"✅ Created channel: {channel_config['name']} in {category_name} at position {channel_index}"
                    self.logger.info(f"[apply_template_from_dir] {msg}")
                    result_msgs.append(msg)
            
            # Check for extra channels in this category
            extra_channels = [
                ch for ch in category.channels if ch.name not in template_channel_names
            ]
            if extra_channels:
                msg = f"⚠️ Extra channels not in template for category '{category_name}': {', '.join(ch.name for ch in extra_channels)}"
                self.logger.warning(f"[apply_template_from_dir] {msg}")
                result_msgs.append(msg)
                view = DeleteExtraObjectsView(extra_channels, object_type_label="channel")
                if interaction:
                    await interaction.followup.send(msg, view=view)
                elif ctx:
                    await ctx.send(msg, view=view)
            
            summary = f"**{category_name}**: {created} created, {updated} updated, {skipped} skipped"
            result_msgs.append(summary)
        
        # Check for extra categories
        extra_categories = [
            cat for cat in guild.categories if cat.name not in template_category_names
        ]
        if extra_categories:
            msg = f"⚠️ Extra categories not in template: {', '.join(cat.name for cat in extra_categories)}"
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(extra_categories, object_type_label="category")
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        
        # Check for orphan channels
        orphan_channels = []
        for ch in guild.channels:
            if getattr(ch, "category", None) is None and isinstance(
                ch, (discord.TextChannel, discord.VoiceChannel)
            ):
                # If template does not support uncategorized channels, all orphans are extra
                # If template_uncategorized_channel_names is empty, all orphans are extra
                if (
                    not template_uncategorized_channel_names
                    or ch.name not in template_uncategorized_channel_names
                ):
                    orphan_channels.append(ch)
        if orphan_channels:
            msg = f"⚠️ Uncategorized channels not in template: {', '.join(ch.name for ch in orphan_channels)}"
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(orphan_channels, object_type_label="channel")
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        if not result_msgs:
            msg = "⚠️ No categories found in template."
            self.logger.warning(f"[apply_template_from_dir] {msg}")
            result_msgs.append(msg)
        return result_msgs

    async def _apply_monolithic_template(self, guild, template_path, ctx=None, interaction=None):
        """Apply a monolithic template.yaml file to the guild."""
        from ..utils.helpers import parse_monolithic_template
        
        result_msgs = []
        template_category_names = set()
        
        try:
            template_config = parse_monolithic_template(template_path)
        except Exception as e:
            msg = f"❌ Failed to parse template: {e}"
            self.logger.error(f"[apply_monolithic_template] {msg}")
            result_msgs.append(msg)
            return result_msgs
        
        # Log template info if available
        if "server" in template_config:
            server_info = template_config["server"]
            if "name" in server_info:
                msg = f"📋 Applying template: {server_info['name']}"
                if "version" in server_info:
                    msg += f" v{server_info['version']}"
                self.logger.info(f"[apply_monolithic_template] {msg}")
                result_msgs.append(msg)
        
        # Process each category
        for category_index, category_config in enumerate(template_config["categories"]):
            category_name = category_config["name"]
            template_category_names.add(category_name)
            
            # Create or update the category
            existing_category = discord.utils.get(guild.categories, name=category_name)
            if existing_category:
                category = existing_category
                msg = f"ℹ️ Category '{category_name}' already exists. Will update channels."
                
                # Check if category is in correct relative order
                desired_yaml_index = category_index
                guild_categories = sorted(guild.categories, key=lambda cat: cat.position)
                current_relative_index = guild_categories.index(category)
                
                if current_relative_index != desired_yaml_index:
                    try:
                        await category.edit(position=desired_yaml_index)
                        msg += f" Moved to position {desired_yaml_index}."
                    except (discord.Forbidden, discord.HTTPException) as e:
                        self.logger.warning(f"Failed to update category position: {e}")
            else:
                category = await guild.create_category(
                    name=category_name, 
                    position=category_index
                )
                msg = f"✅ Created category: {category_name} at position {category_index}"
            
            self.logger.info(f"[apply_monolithic_template] {msg}")
            result_msgs.append(msg)
            
            # Process channels in this category
            created, updated, skipped = 0, 0, 0
            template_channel_names = set()
            
            channels = category_config.get("channels", [])
            for channel_index, channel_config in enumerate(channels):
                channel_name = channel_config["name"]
                template_channel_names.add(channel_name)
                
                # Check if channel exists
                existing_channel = discord.utils.get(category.channels, name=channel_name)
                channel_type = channel_config["type"].lower()
                
                if existing_channel:
                    # Update topic/nsfw and position if needed
                    update_kwargs = {}
                    if (
                        channel_type == "text"
                        and hasattr(existing_channel, "topic")
                        and existing_channel.topic != channel_config.get("topic", "")
                    ):
                        update_kwargs["topic"] = channel_config.get("topic", "")
                    if (
                        channel_type in ("text", "voice")
                        and hasattr(existing_channel, "nsfw")
                        and existing_channel.nsfw != channel_config.get("nsfw", False)
                    ):
                        update_kwargs["nsfw"] = channel_config.get("nsfw", False)
                    
                    # Check if channel is in correct relative order (smart positioning)
                    desired_yaml_index = channel_index
                    if hasattr(existing_channel, "position"):
                        # Get all channels in category sorted by position
                        category_channels = sorted(category.channels, key=lambda ch: ch.position)
                        current_relative_index = category_channels.index(existing_channel)
                        
                        # Only move if the channel is not at the correct relative position
                        if current_relative_index != desired_yaml_index:
                            update_kwargs["position"] = desired_yaml_index
                    
                    if update_kwargs:
                        await existing_channel.edit(**update_kwargs)
                        updated += 1
                        position_msg = f" (position {desired_yaml_index})" if "position" in update_kwargs else ""
                        msg = f"🔄 Updated channel: {existing_channel.name} in {category_name}{position_msg}"
                    else:
                        skipped += 1
                        msg = f"⏭️ Skipped channel (no changes): {existing_channel.name} in {category_name}"
                    
                    self.logger.info(f"[apply_monolithic_template] {msg}")
                    result_msgs.append(msg)
                else:
                    # Create new channel with proper position
                    channel_kwargs = {
                        "name": channel_config["name"],
                        "category": category,
                        "position": channel_index,
                    }
                    
                    if channel_type == "text":
                        if "topic" in channel_config:
                            channel_kwargs["topic"] = channel_config["topic"]
                        if "nsfw" in channel_config:
                            channel_kwargs["nsfw"] = channel_config["nsfw"]
                        await guild.create_text_channel(**channel_kwargs)
                    elif channel_type == "voice":
                        # Voice channels don't support topic, so remove it if present
                        if "topic" in channel_kwargs:
                            del channel_kwargs["topic"]
                        if "nsfw" in channel_config:
                            channel_kwargs["nsfw"] = channel_config["nsfw"]
                        await guild.create_voice_channel(**channel_kwargs)
                    else:
                        msg = f"❌ Unknown channel type: {channel_type} for {channel_config['name']}"
                        self.logger.error(f"[apply_monolithic_template] {msg}")
                        result_msgs.append(msg)
                        skipped += 1
                        continue
                    
                    created += 1
                    msg = f"✅ Created channel: {channel_config['name']} in {category_name} at position {channel_index}"
                    self.logger.info(f"[apply_monolithic_template] {msg}")
                    result_msgs.append(msg)
            
            # Check for extra channels in this category
            extra_channels = [
                ch for ch in category.channels if ch.name not in template_channel_names
            ]
            if extra_channels:
                msg = f"⚠️ Extra channels not in template for category '{category_name}': {', '.join(ch.name for ch in extra_channels)}"
                self.logger.warning(f"[apply_monolithic_template] {msg}")
                result_msgs.append(msg)
                view = DeleteExtraObjectsView(extra_channels, object_type_label="channel")
                if interaction:
                    await interaction.followup.send(msg, view=view)
                elif ctx:
                    await ctx.send(msg, view=view)
            
            summary = f"**{category_name}**: {created} created, {updated} updated, {skipped} skipped"
            result_msgs.append(summary)
        
        # Check for extra categories
        extra_categories = [
            cat for cat in guild.categories if cat.name not in template_category_names
        ]
        if extra_categories:
            msg = f"⚠️ Extra categories not in template: {', '.join(cat.name for cat in extra_categories)}"
            self.logger.warning(f"[apply_monolithic_template] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(extra_categories, object_type_label="category")
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        
        # Check for orphan channels
        orphan_channels = []
        for ch in guild.channels:
            if getattr(ch, "category", None) is None and isinstance(
                ch, (discord.TextChannel, discord.VoiceChannel)
            ):
                orphan_channels.append(ch)
        
        if orphan_channels:
            msg = f"⚠️ Uncategorized channels not in template: {', '.join(ch.name for ch in orphan_channels)}"
            self.logger.warning(f"[apply_monolithic_template] {msg}")
            result_msgs.append(msg)
            view = DeleteExtraObjectsView(orphan_channels, object_type_label="channel")
            if interaction:
                await interaction.followup.send(msg, view=view)
            elif ctx:
                await ctx.send(msg, view=view)
        
        return result_msgs


async def setup(bot: commands.Bot) -> None:
    """Set up the Admin cog."""
    await bot.add_cog(Admin(bot))
