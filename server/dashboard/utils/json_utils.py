

from datetime import datetime
import json
import os
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
import jmespath

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (parent directory)
parent_dir = os.path.dirname(current_dir)

# Convert to string if needed
parent_dir = str(parent_dir)

default_role = {
                "role": "system",
                "content": "you are a professional baller, and you communicate exclusively in a hood language with slang words and such jargon."
            },

def check_user_in_memory(uid):
    data = load_memory_file()
        

def save_json_file_memory(data):
    with open(parent_dir + "/memory/memory.json", "w+") as f:
        json.dump(data, f, indent=4)  


def append_message_to_json_file(user_id, conversation_id, new_message):
    data = load_memory_file()

    data[user_id][conversation_id]["messages"].append(new_message)

    save_json_file_memory(data)

def store_usage_info_data(uid, conversation_id, usage_meta):
    '''    
    structure_example = {
        "uid" : [
            {
                "conversation_id": conversation_id,
                "time": time,
                "usage_meta": {
                    "cost": total_cost,
                    "tokens": total_tokens,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens
                }
            }
        ]
    }
    '''
    with open(parent_dir + "/" + "usage_db/usage_db.json", "r") as f:
        usage_db = json.load(f)
    current_time = datetime.now().strftime('%Y-%m-%d : %H-%M-%S')
    if uid not in usage_db: usage_db[uid] = {}
    if conversation_id not in usage_db[uid]: usage_db[uid][conversation_id] = []
    datapoint = {
        "time":current_time,
        "usage_meta": usage_meta["total"]
    }
    usage_db[uid][conversation_id] = [datapoint] + usage_db[uid][conversation_id]

    with open(parent_dir + "/" + "usage_db/usage_db.json", "w") as f:
        json.dump(usage_db, f, indent=4)



def json_memory_loader(uid, conversation_id, session):
    loaded_memory = universal_memory_searcher(uid, conversation_id)

    memory = []
    if len(loaded_memory) > 21:
        memory.append(loaded_memory[0])
        for i in range(1, 20):
            memory_msg= loaded_memory[-i]
            if memory_msg["role"] == "user":
                session.add_user_message(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                session.add_ai_message(memory_msg["content"])
            memory.append(loaded_memory[-i])
    else:
        for i in loaded_memory:
            memory_msg= i
            if memory_msg["role"] == "user":
                session.add_user_message(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                session.add_ai_message(memory_msg["content"])

    return memory

def json_memory_loader_raw(uid, conversation_id):

    loaded_memory = universal_memory_searcher(uid, conversation_id)

    memory_user = []
    memory_ai = []
    # print(documents)
    if len(loaded_memory) > 21:
        for i in range(1, 20):
            memory_msg= loaded_memory[-i]
            if memory_msg["role"] == "user":
                memory_user.append(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                memory_ai.append(memory_msg["content"])
    else:
        for i in loaded_memory:
            memory_msg= i
            if memory_msg["role"] == "user":
                memory_user.append(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                memory_ai.append(memory_msg["content"])
    # print(memory_user)
    return memory_user, memory_ai


def universal_memory_searcher(uid, conversation_id):
    jq_schema='"{}"."{}".messages[]'.format(uid, conversation_id)
    data = load_memory_file()
    search_results = jmespath.search(jq_schema, data)
    return search_results   

def load_memory_file():
    with open(parent_dir + "/memory/memory.json", "r+") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    j = json_memory_loader_raw("bot.test.paul@gmail.com", "AAPL-2023")
    print(j)