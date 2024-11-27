from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://admin:jgh11DvwDbtfT6Wa@secrag.77916.mongodb.net/?retryWrites=true&w=majority&appName=SECRAG"
database_name = "SECRAG"
collection_name = "messages.authenticated"

# Connect to MongoDB
client = MongoClient(uri)
database = client[database_name]
collection = database[collection_name]

def mongo_insert_user(email):
    """
    Inserts a user with the given email into the database if it doesn't already exist.
    """
    try:
        result = collection.update_one(
            {"_id": email},
            {"$setOnInsert": {"email": email, "chats": []}},  # Add email and an empty chats list
            upsert=True  # Insert only if not exists
        )
        if result.upserted_id:
            print(f"User with email '{email}' inserted.")
        else:
            print(f"User with email '{email}' already exists.")
    except Exception as e:
        print(f"Error inserting user: {e}")


def mongo_insert_chat(email, name, chat_id, filing_date):
    try:
        result = collection.update_one(
            {"_id": email},
            {"$set": {f"chats.{chat_id}": {
                "filing_date": filing_date, 
                "messages": [
                    {"role": "assistant", "content": f"Hello {name}! {chat_id} is embedded and ready for discussion. How can I help you today?"}
                ]
            }}},
            upsert=True
        )
        if result.modified_count > 0: return {"status": "success", "message": f"Chat '{chat_id}' added or updated for user '{email}'."}
        elif result.upserted_id: return {"status": "success", "message": f"User '{email}' created with chat '{chat_id}'."}
        else: return {"status": "unchanged", "message": f"Chat '{chat_id}' already exists for user '{email}'."}
    except Exception as e: return {"status": "error", "message": str(e)}


def mongo_insert_message(email, chat_id, role, content):
    try:
        result = collection.update_one(
            {"_id": email},
            {"$push": {f"chats.{chat_id}.messages": {"role": role, "content": content}}}
        )
        if result.modified_count > 0: return {"status": "success", "message": f"Message added to chat '{chat_id}' for user '{email}'."}
        else: return {"status": "error", "message": f"Chat '{chat_id}' not found for user '{email}'."}
    except Exception as e: return {"status": "error", "message": str(e)}


def mongo_get_chats_by_email(email):
    try:
        user_doc = collection.find_one({"_id": email}, {"chats.chat_id": 1})
        if user_doc and "chats" in user_doc: return [chat["chat_id"] for chat in user_doc["chats"]]
        else: return []

    except Exception as e:
        print(f"Error retrieving chats for email {email}: {e}")
        return []


# Example Usage
if __name__ == "__main__":

    email = 'paul.bezko@hotmail.com'
    name = "Paul Bezko"
    chat_id = 'AAPL-2018-10K'
    filing_date = '2019-10-31'

    role="user"
    content="test"

    # Insert user
    # chats = mongo_get_chats_by_email(email)

    result = mongo_insert_message(email, chat_id, role, content)
    print(result)