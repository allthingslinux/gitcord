"""
Channel management commands cog for GitCord bot.
Contains commands for creating and managing channels and categories.
"""

import yaml

import discord
from discord import app_commands
from discord.ext import commands

from ..utils.helpers import create_embed, parse_channel_config
from ..utils.logger import main_logger as logger
from ..views import DeleteExtraChannelsView


class Channels(commands.Cog):
    """Channel management utility commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the Channels cog."""
        self.bot = bot
        logger.info("Channels cog loaded")

    @commands.command(name='createchannel')
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx: commands.Context) -> None:
        """Create a channel based on properties defined in a YAML file."""
        yaml_path = "/home/user/Projects/gitcord-template/community/off-topic.yaml"

        try:
            # Check if the user has permission to manage channels
            if not ctx.author.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            try:
                channel_config = parse_channel_config(yaml_path)
            except ValueError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=str(e),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Prepare channel creation parameters
            channel_kwargs = {
                'name': channel_config['name'],
                'topic': channel_config.get('topic', ''),
                'nsfw': channel_config.get('nsfw', False)
            }

            # Set position if specified
            if 'position' in channel_config:
                channel_kwargs['position'] = channel_config['position']

            # Create the channel based on type
            if channel_config['type'].lower() == 'text':
                new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
            elif channel_config['type'].lower() == 'voice':
                new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
            else:
                embed = create_embed(
                    title="❌ Invalid Channel Type",
                    description=f"Channel type '{channel_config['type']}' is not supported. "
                                "Use 'text' or 'voice'.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Create success embed
            embed = create_embed(
                title="✅ Channel Created",
                description=f"Successfully created channel: {new_channel.mention}",
                color=discord.Color.green()
            )

            # Add fields manually
            embed.add_field(name="Name", value=channel_kwargs['name'], inline=True)
            embed.add_field(name="Type", value=channel_config['type'], inline=True)
            embed.add_field(name="NSFW", value=channel_kwargs['nsfw'], inline=True)
            embed.add_field(name="Topic", value=channel_config.get('topic', 'No topic set'),
                            inline=False)

            await ctx.send(embed=embed)
            logger.info("Channel '%s' created successfully by %s", channel_config['name'],
                        ctx.author)

        except yaml.YAMLError as e:
            embed = create_embed(
                title="❌ YAML Parse Error",
                description=f"Failed to parse YAML file: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("YAML parse error in createchannel command: %s", e)
        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create channels in this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createchannel command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createchannel command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createchannel command: %s", e)

    @createchannel.error
    async def createchannel_error(self, ctx: commands.Context,
                                  error: commands.CommandError) -> None:
        """Handle errors for the createchannel command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createchannel command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name='createcategory')
    @commands.has_permissions(manage_channels=True)
    async def createcategory(self, ctx: commands.Context) -> None:
        """Create a category and its channels based on properties defined in a YAML file."""
        yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            # Check if the user has permission to manage channels
            if not ctx.author.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=f"Category YAML file not found at: {yaml_path}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=f"Failed to parse YAML file: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Validate required fields
            required_fields = ['name', 'type', 'channels']
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=f"Missing required field: {field}",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return

            # Check if category already exists
            existing_category = discord.utils.get(ctx.guild.categories, name=category_config['name'])
            if existing_category:
                # Category exists, check for differences and apply updates
                
                updated_channels = []
                created_channels = []
                skipped_channels = []
                extra_channels = []
                
                # Get all channels that should exist according to YAML
                yaml_channel_names = set()
                for channel_name in category_config['channels']:
                    try:
                        channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                        channel_config = parse_channel_config(channel_yaml_path)
                        yaml_channel_names.add(channel_config['name'])
                    except Exception as e:
                        logger.error("Failed to parse channel '%s' from YAML: %s", channel_name, e)
                
                # Check for channels that exist in Discord but not in YAML
                for existing_channel in existing_category.channels:
                    if existing_channel.name not in yaml_channel_names:
                        extra_channels.append(existing_channel)
                        logger.info("Found extra channel '%s' in category '%s' (not in YAML)", 
                                  existing_channel.name, category_config['name'])
                
                # Check for category position differences
                category_updated = False
                if existing_category.position != category_config.get('position', 0):
                    try:
                        await existing_category.edit(position=category_config.get('position', 0))
                        category_updated = True
                        logger.info("Updated category '%s' position from %d to %d", 
                                  category_config['name'], existing_category.position, 
                                  category_config.get('position', 0))
                    except Exception as e:
                        logger.error("Failed to update category position: %s", e)

                # Process channels in the category
                for channel_name in category_config['channels']:
                    try:
                        # Construct path to individual channel YAML file
                        channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                        
                        # Parse individual channel configuration
                        channel_config = parse_channel_config(channel_yaml_path)
                        
                        # Check if channel already exists in the category
                        existing_channel = discord.utils.get(existing_category.channels, name=channel_config['name'])
                        
                        if existing_channel:
                            # Channel exists, check for differences and update
                            channel_updated = False
                            update_kwargs = {}
                            
                            # Check topic differences (only for text channels)
                            if hasattr(existing_channel, 'topic') and existing_channel.topic != channel_config.get('topic', ''):
                                update_kwargs['topic'] = channel_config.get('topic', '')
                                channel_updated = True
                            
                            # Check NSFW differences
                            if existing_channel.nsfw != channel_config.get('nsfw', False):
                                update_kwargs['nsfw'] = channel_config.get('nsfw', False)
                                channel_updated = True
                            
                            # Check position differences
                            if 'position' in channel_config and existing_channel.position != channel_config['position']:
                                update_kwargs['position'] = channel_config['position']
                                channel_updated = True
                            
                            # Apply updates if any differences found
                            if channel_updated:
                                try:
                                    await existing_channel.edit(**update_kwargs)
                                    updated_channels.append(existing_channel)
                                    logger.info("Updated channel '%s' in category '%s'", 
                                              channel_config['name'], category_config['name'])
                                except Exception as e:
                                    logger.error("Failed to update channel '%s': %s", channel_config['name'], e)
                                    skipped_channels.append(channel_config['name'])
                            else:
                                skipped_channels.append(channel_config['name'])
                                logger.info("Channel '%s' in category '%s' is already up to date", 
                                          channel_config['name'], category_config['name'])
                        else:
                            # Channel doesn't exist, create it
                            try:
                                channel_kwargs = {
                                    'name': channel_config['name'],
                                    'category': existing_category,
                                    'nsfw': channel_config.get('nsfw', False)
                                }

                                # Add topic only for text channels
                                if channel_config['type'].lower() == 'text':
                                    channel_kwargs['topic'] = channel_config.get('topic', '')

                                if 'position' in channel_config:
                                    channel_kwargs['position'] = channel_config['position']

                                if channel_config['type'].lower() == 'text':
                                    new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
                                elif channel_config['type'].lower() == 'voice':
                                    new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
                                else:
                                    logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                                 channel_name, channel_config['type'])
                                    skipped_channels.append(channel_config['name'])
                                    continue

                                created_channels.append(new_channel)
                                logger.info("Created new channel '%s' in existing category '%s'", 
                                          channel_config['name'], category_config['name'])
                            except Exception as e:
                                logger.error("Failed to create channel '%s': %s", channel_name, e)
                                skipped_channels.append(channel_config['name'])

                    except Exception as e:
                        logger.error("Failed to process channel '%s': %s", channel_name, e)
                        skipped_channels.append(channel_name)
                        continue

                # Create result embed
                embed = create_embed(
                    title="✅ Category Updated",
                    description=f"Successfully processed category: **{existing_category.name}**",
                    color=discord.Color.green()
                )

                # Add fields
                embed.add_field(name="Category", value=existing_category.mention, inline=True)
                if category_updated:
                    embed.add_field(name="Category Updated", value="✅ Position", inline=True)
                else:
                    embed.add_field(name="Category Updated", value="❌ No changes", inline=True)
                
                embed.add_field(name="Channels Created", value=str(len(created_channels)), inline=True)
                embed.add_field(name="Channels Updated", value=str(len(updated_channels)), inline=True)
                embed.add_field(name="Channels Skipped", value=str(len(skipped_channels)), inline=True)
                embed.add_field(name="Extra Channels", value=str(len(extra_channels)), inline=True)

                if created_channels:
                    channel_list = "\n".join([f"• {channel.mention} (new)" for channel in created_channels])
                    embed.add_field(name="New Channels", value=channel_list, inline=False)

                if updated_channels:
                    channel_list = "\n".join([f"• {channel.mention} (updated)" for channel in updated_channels])
                    embed.add_field(name="Updated Channels", value=channel_list, inline=False)

                if extra_channels:
                    channel_list = "\n".join([f"• {channel.mention} (not in YAML)" for channel in extra_channels])
                    embed.add_field(name="Extra Channels (Not in YAML)", value=channel_list, inline=False)
                
                # Add delete button if there are extra channels
                if extra_channels:
                    delete_view = DeleteExtraChannelsView(extra_channels, existing_category.name)
                    await ctx.send(embed=embed, view=delete_view)
                else:
                    await ctx.send(embed=embed)
                logger.info("Category '%s' processed: %d created, %d updated, %d skipped, %d extra", 
                           category_config['name'], len(created_channels), len(updated_channels), 
                           len(skipped_channels), len(extra_channels))
                return

            # Create the category (original logic for new categories)
            category_kwargs = {
                'name': category_config['name'],
                'position': category_config.get('position', 0)
            }

            new_category = await ctx.guild.create_category(**category_kwargs)
            created_channels = []

            # Create channels within the category
            for channel_name in category_config['channels']:
                try:
                    # Construct path to individual channel YAML file
                    channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                    
                    # Parse individual channel configuration
                    channel_config = parse_channel_config(channel_yaml_path)
                    
                    # Check if channel already exists in the category
                    existing_channel = discord.utils.get(new_category.channels, name=channel_config['name'])
                    if existing_channel:
                        logger.warning("Channel '%s' already exists in category '%s', skipping", 
                                     channel_config['name'], category_config['name'])
                        continue
                    
                    # Prepare channel creation parameters
                    channel_kwargs = {
                        'name': channel_config['name'],
                        'category': new_category,
                        'nsfw': channel_config.get('nsfw', False)
                    }

                    # Add topic only for text channels
                    if channel_config['type'].lower() == 'text':
                        channel_kwargs['topic'] = channel_config.get('topic', '')

                    # Set position if specified
                    if 'position' in channel_config:
                        channel_kwargs['position'] = channel_config['position']

                    # Create the channel based on type
                    if channel_config['type'].lower() == 'text':
                        new_channel = await ctx.guild.create_text_channel(**channel_kwargs)
                    elif channel_config['type'].lower() == 'voice':
                        new_channel = await ctx.guild.create_voice_channel(**channel_kwargs)
                    else:
                        logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                     channel_name, channel_config['type'])
                        continue

                    created_channels.append(new_channel)
                    logger.info("Channel '%s' created successfully in category '%s'", 
                              channel_config['name'], category_config['name'])

                except Exception as e:
                    logger.error("Failed to create channel '%s': %s", channel_name, e)
                    continue

            # Create success embed
            embed = create_embed(
                title="✅ Category Created",
                description=f"Successfully created category: **{new_category.name}**",
                color=discord.Color.green()
            )

            # Add fields
            embed.add_field(name="Category Name", value=new_category.name, inline=True)
            embed.add_field(name="Category Type", value=category_config['type'], inline=True)
            embed.add_field(name="Position", value=category_config.get('position', 0), inline=True)
            embed.add_field(name="Channels Created", value=f"{len(created_channels)}/{len(category_config['channels'])}", inline=False)

            if created_channels:
                channel_list = "\n".join([f"• {channel.mention}" for channel in created_channels])
                embed.add_field(name="Created Channels", value=channel_list, inline=False)

            await ctx.send(embed=embed)
            logger.info("Category '%s' with %d channels created successfully by %s", 
                       category_config['name'], len(created_channels), ctx.author)

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create categories or channels in this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Permission error in createcategory command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Discord HTTP error in createcategory command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error("Unexpected error in createcategory command: %s", e)

    @createcategory.error
    async def createcategory_error(self, ctx: commands.Context,
                                   error: commands.CommandError) -> None:
        """Handle errors for the createcategory command."""
        if isinstance(error, commands.MissingPermissions):
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error("Error in createcategory command: %s", error)
            await ctx.send(f"An error occurred: {error}")

    @app_commands.command(name="createcategory", description="Create a category and its channels from YAML configuration")
    @app_commands.describe(yaml_path="Path to the category YAML file (optional)")
    async def createcategory_slash(self, interaction: discord.Interaction, yaml_path: str | None = None) -> None:
        """Slash command to create a category and its channels based on YAML configuration."""
        await interaction.response.defer()

        # Use default path if none provided
        if yaml_path is None:
            yaml_path = "/home/user/Projects/gitcord-template/community/category.yaml"

        try:
            # Check if the user has permission to manage channels
            if not interaction.user.guild_permissions.manage_channels:
                embed = create_embed(
                    title="❌ Permission Denied",
                    description="You need the 'Manage Channels' permission to use this command.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Parse category configuration
            try:
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    category_config = yaml.safe_load(file)
            except FileNotFoundError:
                embed = create_embed(
                    title="❌ File Not Found",
                    description=f"Category YAML file not found at: {yaml_path}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            except yaml.YAMLError as e:
                embed = create_embed(
                    title="❌ Invalid YAML",
                    description=f"Failed to parse YAML file: {str(e)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Validate required fields
            required_fields = ['name', 'type', 'channels']
            for field in required_fields:
                if field not in category_config:
                    embed = create_embed(
                        title="❌ Invalid Configuration",
                        description=f"Missing required field: {field}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return

            # Check if category already exists
            existing_category = discord.utils.get(interaction.guild.categories, name=category_config['name'])
            if existing_category:
                # Category exists, check for differences and apply updates
                
                updated_channels = []
                created_channels = []
                skipped_channels = []
                extra_channels = []
                
                # Get all channels that should exist according to YAML
                yaml_channel_names = set()
                for channel_name in category_config['channels']:
                    try:
                        channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                        channel_config = parse_channel_config(channel_yaml_path)
                        yaml_channel_names.add(channel_config['name'])
                    except Exception as e:
                        logger.error("Failed to parse channel '%s' from YAML: %s", channel_name, e)
                
                # Check for channels that exist in Discord but not in YAML
                for existing_channel in existing_category.channels:
                    if existing_channel.name not in yaml_channel_names:
                        extra_channels.append(existing_channel)
                        logger.info("Found extra channel '%s' in category '%s' (not in YAML)", 
                                  existing_channel.name, category_config['name'])
                
                # Check for category position differences
                category_updated = False
                if existing_category.position != category_config.get('position', 0):
                    try:
                        await existing_category.edit(position=category_config.get('position', 0))
                        category_updated = True
                        logger.info("Updated category '%s' position from %d to %d", 
                                  category_config['name'], existing_category.position, 
                                  category_config.get('position', 0))
                    except Exception as e:
                        logger.error("Failed to update category position: %s", e)

                # Process channels in the category
                for channel_name in category_config['channels']:
                    try:
                        # Construct path to individual channel YAML file
                        channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                        
                        # Parse individual channel configuration
                        channel_config = parse_channel_config(channel_yaml_path)
                        
                        # Check if channel already exists in the category
                        existing_channel = discord.utils.get(existing_category.channels, name=channel_config['name'])
                        
                        if existing_channel:
                            # Channel exists, check for differences and update
                            channel_updated = False
                            update_kwargs = {}
                            
                            # Check topic differences (only for text channels)
                            if hasattr(existing_channel, 'topic') and existing_channel.topic != channel_config.get('topic', ''):
                                update_kwargs['topic'] = channel_config.get('topic', '')
                                channel_updated = True
                            
                            # Check NSFW differences
                            if existing_channel.nsfw != channel_config.get('nsfw', False):
                                update_kwargs['nsfw'] = channel_config.get('nsfw', False)
                                channel_updated = True
                            
                            # Check position differences
                            if 'position' in channel_config and existing_channel.position != channel_config['position']:
                                update_kwargs['position'] = channel_config['position']
                                channel_updated = True
                            
                            # Apply updates if any differences found
                            if channel_updated:
                                try:
                                    await existing_channel.edit(**update_kwargs)
                                    updated_channels.append(existing_channel)
                                    logger.info("Updated channel '%s' in category '%s'", 
                                              channel_config['name'], category_config['name'])
                                except Exception as e:
                                    logger.error("Failed to update channel '%s': %s", channel_config['name'], e)
                                    skipped_channels.append(channel_config['name'])
                            else:
                                skipped_channels.append(channel_config['name'])
                                logger.info("Channel '%s' in category '%s' is already up to date", 
                                          channel_config['name'], category_config['name'])
                        else:
                            # Channel doesn't exist, create it
                            try:
                                channel_kwargs = {
                                    'name': channel_config['name'],
                                    'category': existing_category,
                                    'nsfw': channel_config.get('nsfw', False)
                                }

                                # Add topic only for text channels
                                if channel_config['type'].lower() == 'text':
                                    channel_kwargs['topic'] = channel_config.get('topic', '')

                                if 'position' in channel_config:
                                    channel_kwargs['position'] = channel_config['position']

                                if channel_config['type'].lower() == 'text':
                                    new_channel = await interaction.guild.create_text_channel(**channel_kwargs)
                                elif channel_config['type'].lower() == 'voice':
                                    new_channel = await interaction.guild.create_voice_channel(**channel_kwargs)
                                else:
                                    logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                                 channel_name, channel_config['type'])
                                    skipped_channels.append(channel_config['name'])
                                    continue

                                created_channels.append(new_channel)
                                logger.info("Created new channel '%s' in existing category '%s'", 
                                          channel_config['name'], category_config['name'])
                            except Exception as e:
                                logger.error("Failed to create channel '%s': %s", channel_name, e)
                                skipped_channels.append(channel_config['name'])

                    except Exception as e:
                        logger.error("Failed to process channel '%s': %s", channel_name, e)
                        skipped_channels.append(channel_name)
                        continue

                # Create result embed
                embed = create_embed(
                    title="✅ Category Updated",
                    description=f"Successfully processed category: **{existing_category.name}**",
                    color=discord.Color.green()
                )

                # Add fields
                embed.add_field(name="Category", value=existing_category.mention, inline=True)
                if category_updated:
                    embed.add_field(name="Category Updated", value="✅ Position", inline=True)
                else:
                    embed.add_field(name="Category Updated", value="❌ No changes", inline=True)
                
                embed.add_field(name="Channels Created", value=str(len(created_channels)), inline=True)
                embed.add_field(name="Channels Updated", value=str(len(updated_channels)), inline=True)
                embed.add_field(name="Channels Skipped", value=str(len(skipped_channels)), inline=True)
                embed.add_field(name="Extra Channels", value=str(len(extra_channels)), inline=True)

                if created_channels:
                    channel_list = "\n".join([f"• {channel.mention} (new)" for channel in created_channels])
                    embed.add_field(name="New Channels", value=channel_list, inline=False)

                if updated_channels:
                    channel_list = "\n".join([f"• {channel.mention} (updated)" for channel in updated_channels])
                    embed.add_field(name="Updated Channels", value=channel_list, inline=False)

                if extra_channels:
                    channel_list = "\n".join([f"• {channel.mention} (not in YAML)" for channel in extra_channels])
                    embed.add_field(name="Extra Channels (Not in YAML)", value=channel_list, inline=False)

                # Add delete button if there are extra channels
                if extra_channels:
                    delete_view = DeleteExtraChannelsView(extra_channels, existing_category.name)
                    await interaction.followup.send(embed=embed, view=delete_view)
                else:
                    await interaction.followup.send(embed=embed)
                    
                logger.info("Category '%s' processed: %d created, %d updated, %d skipped, %d extra", 
                           category_config['name'], len(created_channels), len(updated_channels), 
                           len(skipped_channels), len(extra_channels))
                return

            # Create the category (original logic for new categories)
            category_kwargs = {
                'name': category_config['name'],
                'position': category_config.get('position', 0)
            }

            new_category = await interaction.guild.create_category(**category_kwargs)
            created_channels = []

            # Create channels within the category
            for channel_name in category_config['channels']:
                try:
                    # Construct path to individual channel YAML file
                    channel_yaml_path = f"/home/user/Projects/gitcord-template/community/{channel_name}.yaml"
                    
                    # Parse individual channel configuration
                    channel_config = parse_channel_config(channel_yaml_path)
                    
                    # Check if channel already exists in the category
                    existing_channel = discord.utils.get(new_category.channels, name=channel_config['name'])
                    if existing_channel:
                        logger.warning("Channel '%s' already exists in category '%s', skipping", 
                                     channel_config['name'], category_config['name'])
                        continue
                    
                    # Prepare channel creation parameters
                    channel_kwargs = {
                        'name': channel_config['name'],
                        'category': new_category,
                        'nsfw': channel_config.get('nsfw', False)
                    }

                    # Add topic only for text channels
                    if channel_config['type'].lower() == 'text':
                        channel_kwargs['topic'] = channel_config.get('topic', '')

                    # Set position if specified
                    if 'position' in channel_config:
                        channel_kwargs['position'] = channel_config['position']

                    # Create the channel based on type
                    if channel_config['type'].lower() == 'text':
                        new_channel = await interaction.guild.create_text_channel(**channel_kwargs)
                    elif channel_config['type'].lower() == 'voice':
                        new_channel = await interaction.guild.create_voice_channel(**channel_kwargs)
                    else:
                        logger.warning("Skipping channel '%s': Invalid type '%s'", 
                                     channel_name, channel_config['type'])
                        continue

                    created_channels.append(new_channel)
                    logger.info("Channel '%s' created successfully in category '%s'", 
                              channel_config['name'], category_config['name'])

                except Exception as e:
                    logger.error("Failed to create channel '%s': %s", channel_name, e)
                    continue

            # Create success embed
            embed = create_embed(
                title="✅ Category Created",
                description=f"Successfully created category: **{new_category.name}**",
                color=discord.Color.green()
            )

            # Add fields
            embed.add_field(name="Category Name", value=new_category.name, inline=True)
            embed.add_field(name="Category Type", value=category_config['type'], inline=True)
            embed.add_field(name="Position", value=category_config.get('position', 0), inline=True)
            embed.add_field(name="Channels Created", value=f"{len(created_channels)}/{len(category_config['channels'])}", inline=False)

            if created_channels:
                channel_list = "\n".join([f"• {channel.mention}" for channel in created_channels])
                embed.add_field(name="Created Channels", value=channel_list, inline=False)

            await interaction.followup.send(embed=embed)
            logger.info("Category '%s' with %d channels created successfully by %s", 
                       category_config['name'], len(created_channels), interaction.user)

        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to create categories or channels in this server.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Permission error in createcategory slash command")
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Discord Error",
                description=f"Discord API error: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Discord HTTP error in createcategory slash command: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            logger.error("Unexpected error in createcategory slash command: %s", e)


async def setup(bot: commands.Bot) -> None:
    """Set up the Channels cog."""
    await bot.add_cog(Channels(bot)) 