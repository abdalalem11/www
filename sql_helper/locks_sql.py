# تخزين بسيط للأقفال في ملف JSON
import json
import os

LOCKS_FILE = "locks.json"

def load_locks():
    if os.path.exists(LOCKS_FILE):
        try:
            with open(LOCKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_locks(data):
    with open(LOCKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_locks(chat_id):
    data = load_locks()
    return data.get(str(chat_id), {})

def is_locked(chat_id, lock_type):
    data = load_locks()
    return data.get(str(chat_id), {}).get(lock_type, False)

def update_lock(chat_id, lock_type, value):
    data = load_locks()
    if str(chat_id) not in data:
        data[str(chat_id)] = {}
    data[str(chat_id)][lock_type] = value
    save_locks(data)
