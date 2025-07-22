"""
File path constants for GitCord bot.
"""

import os

# GitCord data directory for storing per-guild template repositories and metadata
GITCORD_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".gitcord_data")
os.makedirs(GITCORD_DATA_DIR, exist_ok=True)

def get_template_repo_dir(guild_id):
    """Get the template repository directory for a specific guild."""
    return os.path.join(GITCORD_DATA_DIR, "template_repo", str(guild_id))

def get_metadata_file(guild_id):
    """Get the metadata file path for a specific guild."""
    return os.path.join(GITCORD_DATA_DIR, f"template_source_{guild_id}.json")
