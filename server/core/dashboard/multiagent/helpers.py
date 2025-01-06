import json
import os
from typing import Dict, List

JSON_FILE_PATH = "server/memory/anonymous_chats_db.json"

def load_json() -> Dict[str, List[str]]:
    with open(JSON_FILE_PATH, 'r') as file:
        return json.load(file)

# Retrieve chats based on the input key
def get_chats_by_key(key: str) -> List[str]:
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)
    return data.get(key, [])

# Add a message to the chat based on input key
def add_message(key: str, message: dict):
    data = load_json()
    if key not in data:
        data[key] = []
    data[key].append(message)
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)
    return data[key]

def create_file_if_not_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({}, file)
              # Just create an empty file
        print(f"File '{file_path}' created.")
    else:
        print(f"File '{file_path}' already exists.")