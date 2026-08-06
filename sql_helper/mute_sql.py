import json
import os

MUTE_FILE = "mute.json"

def load_mutes():
    if os.path.exists(MUTE_FILE):
        try:
            with open(MUTE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mutes(data):
    with open(MUTE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def is_muted(chat_id, user_id):
    data = load_mutes()
    return data.get(str(chat_id), {}).get(str(user_id), False)

def mute(chat_id, user_id):
    data = load_mutes()
    if str(chat_id) not in data:
        data[str(chat_id)] = {}
    data[str(chat_id)][str(user_id)] = True
    save_mutes(data)

def unmute(chat_id, user_id):
    data = load_mutes()
    if str(chat_id) in data and str(user_id) in data[str(chat_id)]:
        del data[str(chat_id)][str(user_id)]
        save_mutes(data)
