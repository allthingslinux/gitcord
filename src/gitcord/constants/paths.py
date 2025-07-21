"""
File path constants for GitCord bot.
"""

import os

# Default YAML file paths
CATEGORY_YAML_PATH = "/home/user/Projects/gitcord-template/community/category.yaml"
OFFTOPIC_YAML_PATH = "/home/user/Projects/gitcord-template/community/off-topic.yaml"
TEMPLATE_DIR = "/home/user/Projects/gitcord-template/community/"

# Add more paths as needed
GITCORD_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".gitcord_data")
os.makedirs(GITCORD_DATA_DIR, exist_ok=True)

def get_template_repo_dir(guild_id):
    return os.path.join(GITCORD_DATA_DIR, "template_repo", str(guild_id))

def get_metadata_file(guild_id):
    return os.path.join(GITCORD_DATA_DIR, f"template_source_{guild_id}.json")
