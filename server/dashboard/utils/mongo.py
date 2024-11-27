from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://admin:jgh11DvwDbtfT6Wa@secrag.77916.mongodb.net/?retryWrites=true&w=majority&appName=SECRAG"
database_name = "SECRAG"
collection_name = "messages.authenticated"


# Connect to MongoDB
client = MongoClient(uri)
database = client["SECRAG"]
collection = database["messages.authenticated"]


def mongo_get_chats_by_user_id(collection, user_id):
    try:
        user_doc = collection.find_one({"_id": user_id}, {"chats": 1})
        if user_doc and "chats" in user_doc:
            return list(user_doc["chats"].keys())
        else: 
            return []
    except Exception as e:
        return {"error": f"Error retrieving chats for user_id '{user_id}': {str(e)}"}

def mongo_get_messages_by_chat(collection, user_id, chat_id):
    try:
        projection = {f"chats.{chat_id}": 1}
        user_doc = collection.find_one({"_id": user_id}, projection)
        if user_doc and "chats" in user_doc and chat_id in user_doc["chats"]:
            chat = user_doc["chats"][chat_id]
            return {"filing_date": chat["filing_date"], "messages": chat["messages"]}
        else: 
            return {"error": f"Chat not found for user_id '{user_id}'."}
    except Exception as e: 
        return {"error": f"Error retrieving messages for user_id '{user_id}' and chat '{chat}': {str(e)}"}

def mongo_insert_chat(collection, user_id, name, chat_id, filing_date):
    try:
        result = collection.update_one(
            {"_id": user_id},
            {"$set": {f"chats.{chat_id}": {
                "filing_date": filing_date, 
                "messages": [{"role": "assistant", "content": f"Hello {name}! {chat_id} is embedded and ready for discussion. How can I help you today?"}]
            }}},
            upsert=True
        )
        if result.modified_count > 0: 
            return {"message": f"Chat '{chat_id}' added or updated for user '{user_id}'."}
        elif result.upserted_id: 
            return {"message": f"User '{user_id}' created with chat '{chat_id}'."}
        else:
            return {"message": f"Chat '{chat_id}' already exists for user '{user_id}'."}
    except Exception as e: 
        return {"error": f"Error creating chat for '{user_id}' and chat '{chat_id}': {str(e)}"}

def mongo_insert_message(collection, user_id, chat_id, role, content):
    try:
        result = collection.update_one(
            {"_id": user_id},
            {"$push": {f"chats.{chat_id}.messages": {"role": role, "content": content}}}
        )
        if result.modified_count > 0: 
            return {"message": f"Message added to chat '{chat_id}' for user '{user_id}'."}
        else: 
            return {"error": f"Chat '{chat_id}' not found for user '{user_id}'."}
    except Exception as e:
        return {"error": f"Error inserting message for '{user_id}' and chat '{chat_id}' and message '{content}': {str(e)}"}

def mongo_delete_chat(collection, user_id, chat_id):
    try:
        result = collection.update_one(
            {"_id": user_id},
            {"$unset": {f"chats.{chat_id}": ""}}
        )
        if result.modified_count > 0:
            return {"message": f"Chat '{chat_id}' deleted for user '{user_id}'."}
        else:
            return {"error": f"Chat '{chat_id}' not found for user '{user_id}'."}
    except Exception as e:
        return {"error": f"Error deleting chat for '{user_id}' and chat '{chat_id}': {str(e)}"}

def mongo_reset_chat(collection, user_id, chat_id):
    try:
        user_doc = collection.find_one({"_id": user_id}, {f"chats.{chat_id}.messages": 1})
        if user_doc and "chats" in user_doc and chat_id in user_doc["chats"]:
            messages = user_doc["chats"][chat_id].get("messages", [])
            if messages:
                first_message = messages[0]
                result = collection.update_one(
                    {"_id": user_id},
                    {"$set": {f"chats.{chat_id}.messages": [first_message]}}
                )
                if result.modified_count > 0:
                    return {"message": f"Chat '{chat_id}' refreshed for user '{user_id}'."}
                return {"message": f"No changes made to chat '{chat_id}' for user '{user_id}'."}
            return {"error": f"Chat '{chat_id}' has no messages to retain."}
        return {"error": f"Chat '{chat_id}' not found for user '{user_id}'."}
    except Exception as e:
        return {"error": f"Error refreshing chat '{chat_id}' for user '{user_id}': {str(e)}"}

def mongo_log_response(response):
    if 'error' in response:
        print(response['error'])
    elif 'message' in response:
        print(response['message'])
