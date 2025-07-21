import os
import json

def get_metadata_file(guild_id):
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, f".template_source_{guild_id}.json")

def save_metadata(guild_id, data):
    with open(get_metadata_file(guild_id), "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_metadata(guild_id):
    path = get_metadata_file(guild_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_metadata(guild_id, key, value):
    data = load_metadata(guild_id) or {}
    data[key] = value
    save_metadata(guild_id, data)

def clear_metadata(guild_id):
    path = get_metadata_file(guild_id)
    if os.path.exists(path):
        os.remove(path) 