import json
import os
from typing import Dict, List, Literal
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from globals import tools_triggering_plotter, tool_call_strings

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

def should_call_plotter(messages: list) -> bool:
    for message in messages:
        if isinstance(message, ToolMessage):
            if message.name in tools_triggering_plotter:
                return True
    return False

def get_last_message(messages: list, type: Literal["user", "ai"]) -> bool:
    last_message = None
    for message in messages:
        if (type == "user" and isinstance(message, HumanMessage)) or (type == "ai" and isinstance(message, AIMessage)):
            last_message = message
    if last_message:
        return last_message
    
    raise Exception(f"No {type} message found")

def get_last_node_message(messages: list, node_name: Literal["concierge", "archivist", "plotter"]) -> bool:
    last_message = AIMessage(content="")
    for message in messages:
        if isinstance(message, AIMessage) and message.name == node_name:
            last_message = message

    return last_message

def flowstep_string_state_machine(tool_call_data: dict):
        flowstep_strings = []

        for i in tool_call_data["buffer"]:
            print(i)
            tool_call_buffer_data = json.loads(i)       
            if tool_call_data["name"] == "retrieve_data_from_filing":           
                flowstep_string = f"Reading {tool_call_buffer_data['tool_input']['filing_type']} filing from {tool_call_buffer_data['tool_input']['filing_date']}... "

            elif tool_call_data["name"] == "search_tickers":
                flowstep_string = f"Retrieving ticker for {tool_call_buffer_data['query']}... "

            elif tool_call_data["name"] == "get_available_filings":
                flowstep_string = f"Retrieving available {tool_call_buffer_data['year']} filings for {tool_call_buffer_data['ticker']}... "

            elif tool_call_data["name"] == "ticker_news":
                flowstep_string = f"Searching news for {tool_call_buffer_data['query']}... "

            else:
                flowstep_string = tool_call_strings[tool_call_data["name"]]+"... "
            flowstep_strings.append(flowstep_string)
        return flowstep_strings

