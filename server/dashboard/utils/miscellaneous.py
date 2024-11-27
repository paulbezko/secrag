from fastapi import Request
import json

def save_message(email, chat, role, message):

    with open("database/memory/chats.json", "r") as file: chat_memory = json.load(file)
    chat_memory[email][chat]["messages"].append({"role": role, "content": message})
    with open("database/memory/chats.json", "w") as f: json.dump(chat_memory, f, indent=4)

def get_user_ip(request: Request):
    ip_address = request.client.host

    # For apps behind a reverse proxy, check headers
    forwarded_ip = request.headers.get('X-Forwarded-For')
    real_ip = request.headers.get('X-Real-IP')

    # Prefer header values if they exist (proxy scenario)
    user_ip = forwarded_ip or real_ip or ip_address
    return user_ip