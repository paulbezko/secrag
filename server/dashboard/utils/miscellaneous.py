import json

def save_message(email, chat, role, message):

    with open("database/memory/chats.json", "r") as file: chat_memory = json.load(file)
    chat_memory[email][chat]["messages"].append({"role": role, "content": message})
    with open("database/memory/chats.json", "w") as f: json.dump(chat_memory, f, indent=4)