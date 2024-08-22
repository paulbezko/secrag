

import json
from utils.vectorstore_utils import load_sec
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter

default_role = {
                "role": "system",
                "content": "you are a professional baller, and you communicate exclusively in a hood language with slang words and such jargon."
            },

def load_json_file_memory(uid, conversation_id, conversation_highlight, create_on_error = True):
    with open("memory/{}_memory.json".format(uid), "a+") as f:
        pass
    
    with open("memory/{}_memory.json".format(uid), "r+") as f:
        try:
            data = json.load(f)
            return data
        except Exception as e:
            print("FAULT: ", e)
            if not create_on_error:
                return {}
            conversation_id = conversation_id if conversation_id != None else 0
            data ={"conversations":[                        
                {"conversation_{}".format(conversation_id): {
                    "highlight": conversation_highlight,
                    "messages": [
                                {
                                    "role": "system",
                                    "content": "you are a professional baller, and you communicate exclusively in a hood language with slang words and such jargon."
                                },
                            ]
                        }
                    }
                ]      
            }
            json.dump(data, f, indent=4) 
            return data

def init_load_json_file_memory(uid, conversation_id, conversation_highlight, ticker = None, filing = None, create_on_error = True):
    with open("memory/{}_memory.json".format(uid), "a+") as f:
        pass
    
    with open("memory/{}_memory.json".format(uid), "r+") as f:
        try:
            data = json.load(f)
            return data, conversation_id
        except Exception as e:
            print("FAULT: ", e)
            if not ticker and not filing:
                raise Exception("Missing Ticker or Filing for conversation initialization")
            if not create_on_error:
                return {}
            conversation_id = conversation_id if conversation_id != None else 0
            data ={"conversations":[                        
                {"conversation_{}".format(conversation_id): {
                    "highlight": conversation_highlight,
                    "ticker": ticker,
                    "filing": filing,
                    "messages": [
                                {
                                    "role": "system",
                                    "content": "you are a professional baller, and you communicate exclusively in a hood language with slang words and such jargon."
                                },
                            ]
                        }
                    }
                ]      
            }
            json.dump(data, f, indent=4) 
            return data, conversation_id         

def save_json_file_memory(data, uid):
    with open("memory/{}_memory.json".format(uid), "w+") as f:
        json.dump(data, f, indent=4)  


def conversation_handler_json(user_id, conversation_id, conversation_highlight, ticker, filing):
    data = load_json_file_memory(user_id, conversation_id, conversation_highlight, create_on_error=False)
    conversation_found = False
    conversation_id_max = 0
    for i in data["conversations"]:
        conversation_id_max += 1
        if "conversation_{}".format(conversation_id) in i.keys():
            print("Conversation found")
            conversation_found = True
            break
    if conversation_found == False:
        print("Conversation not found")
        conversation_id = conversation_id_max + 1
        data["conversations"].append({
                "conversation_{}".format(conversation_id): {
                    "highlight": conversation_highlight,
                    "ticker": ticker,
                    "filing": filing,
                    "messages": [                                
                                    {
                                        "role": "system",
                                        "content": "you are a financial expert answering questions on SEC report filings."
                                    }
                                ]
                }
            })
        save_json_file_memory(data, user_id)
    return conversation_id
    
def append_message_to_user(users, user_id, new_message):
    # Traverse the list of users to find the object with the specified user_id
    user_id_str = str(user_id)
    for user in users:
        if user_id_str in user:
            # Append the new message to the user's messages array
            user[user_id_str]['conversation'].append(new_message)
            return users
            
    return users


def append_message_to_json_file(user_id, conversation_id, new_message):
    data = load_json_file_memory(user_id, conversation_id, "", create_on_error=False)
    
    # Append the new message to the user's messages
    if "conversations" in data:
        for i in data["conversations"]:
            if "conversation_{}".format(conversation_id) in i.keys():
                i["conversation_{}".format(conversation_id)]["messages"].append(new_message)
                break
        # data["conversations"]["conversation_{}".format(conversation_id)]["messages"].append(new_message)
    
    # Save the updated data back to the file
    save_json_file_memory(data, user_id)
    
def append_user_to_json_file(user_id):
    data = load_json_file_memory(0)
    new_message =   {
                        "role": "system",
                        "content": "you are a professional baller, and you communicate exclusively in a hood language with slang words and such jargon."
                    }
    # Append the new message to the user's messages
    if "users" in data:
        data["users"] = append_message_to_user(data["users"], user_id, new_message, new_user = True)
    
    # Save the updated data back to the file
    save_json_file_memory(data, 0)

def check_user_in_json_file(user_id):
    data = load_json_file_memory(0)
    
    # Append the new message to the user's messages
    if "users" in data:
        if user_id in data["users"]:
            return True
        else:
            return False

def get_conversation_from_json_file(user_id, conversation_id):
    data = load_json_file_memory()
    
    if "users" in data:
        if user_id in data["users"]:
            if conversation_id in data["users"][user_id]["conversations"]["id"]:
                return data["users"][user_id]["conversations"][conversation_id]
            else:
                return False
        else:
            return False
    else:
        return False



def append_to_json_file(uid, new_value):
    data = load_json_file_memory(uid)
    
    # Determine the next available ID
    if data:
        max_id = max(int(id) for id in data.keys())
        next_id = str(max_id + 1)
    else:
        next_id = "1"  # Start with ID 1 if the file is empty or doesn't exist
    
    # Append the new value with the next available ID
    data["users"][next_id] = new_value
    
    # Save the updated data back to the file
    save_json_file_memory(data, uid) 

def retrieve_conversation_filing_info(uid, conversation_id):
    with open("memory/{}_memory.json".format(uid), "r+") as f:
        data = json.load(f)
        
    # Find matching conversation
    for i in data["conversations"]:
        if "conversation_{}".format(conversation_id) in i.keys():
            # Get filing data from the conversation
            ticker = i["conversation_{}".format(conversation_id)]["ticker"]
            filing = i["conversation_{}".format(conversation_id)]["filing"]
            return ticker, filing
    raise Exception("Could not find conversation for user - {} with id - {}".format(uid, conversation_id))
        
def json_splitter(uid, conversation_id, prompt):
    jq_schema=".conversations[].conversation_{}.messages[]?".format(conversation_id)
    loader = JSONLoader("memory/{}_memory.json".format(uid), jq_schema=jq_schema, text_content=False)
    documents = loader.load()
    documents_used = []
    memory = {"chat_history":[]}
    if len(documents) > 21:
        memory["chat_history"].append(documents[0].page_content)
        for i in range(1, 20):
            memory["chat_history"].append(documents[-i].page_content)
        documents_used.append(documents[0])
        documents_used.extend(documents[-21:])
    else:
        for i in documents:
            memory["chat_history"].append(i.page_content)
        documents_used = documents
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents_used)
    if docs == []:
        append_user_to_json_file(uid)
        docs = json_splitter(uid)
    return docs, memory

def process_json_memory(json_memory, memory):
    processed_input_memory = []
    processed_output_memory = []
    prompt = ""
    for message in json_memory["chat_history"]:
        json_message = json.loads(message)
        if json_message["role"] == "system":
            propmt = json_message["content"]
        if json_message["role"] == "user":            
            processed_input_memory.append({"input": json_message["content"]})
        if json_message["role"] == "assistant":
            processed_output_memory.append({"answer": json_message["content"]})
    return processed_input_memory, processed_output_memory, prompt

def json_memory_loader(uid, conversation_id, session):
    jq_schema=".conversations[].conversation_{}.messages[]?".format(conversation_id)
    loader = JSONLoader("memory/{}_memory.json".format(uid), jq_schema=jq_schema, text_content=False)
    documents = loader.load()
    memory = []
    if len(documents) > 21:
        memory.append(documents[0].page_content)
        for i in range(1, 20):
            memory_msg= json.loads(documents[-i].page_content)
            if memory_msg["role"] == "user":
                session.add_user_message(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                session.add_ai_message(memory_msg["content"])
            memory.append(documents[-i].page_content)
    else:
        for i in documents:
            memory_msg= json.loads(i.page_content)
            if memory_msg["role"] == "user":
                session.add_user_message(memory_msg["content"])
            if memory_msg["role"] == "assistant":
                session.add_ai_message(memory_msg["content"])

    return memory