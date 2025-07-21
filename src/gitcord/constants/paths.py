"""
File path constants for GitCord bot.
"""

import os

# Default YAML file paths
CATEGORY_YAML_PATH = "/home/user/Projects/gitcord-template/community/category.yaml"
OFFTOPIC_YAML_PATH = "/home/user/Projects/gitcord-template/community/off-topic.yaml"
TEMPLATE_DIR = "/home/user/Projects/gitcord-template/community/"

# Add more paths as needed
def get_template_repo_dir(guild_id):
    import os
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, ".template_repo", str(guild_id))
