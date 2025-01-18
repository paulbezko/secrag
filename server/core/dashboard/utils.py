from ...globals import stop_signals, mongo, config

from datetime import datetime
import time

async def get_assistant_response_old(socket_id, input):
    if input == "I'd like to sign up":
        response = "Sure! Enter your email below to start."
        signal_payload = {'signal_type': 'signup_email'}
        suggestions = []
    
    elif input == "I'd like to sign in":
        response = "Of course! Enter your email and password below."
        signal_payload = {'signal_type': 'login'}
        suggestions = ['I forgot my password']

    elif input == "I forgot my password":
        response = "No worries. Enter your email below and we'll send you a reset link."
        signal_payload = {'signal_type': 'forgot_password'}
        suggestions = []

    elif input == "I'd like to know more about the pricing":
        response = "Sure! Here's the pricing plan."
        signal_payload = {}
        suggestions = ['Ass?']
    
    elif input == "I'd like to contact you":
        response = "Of course! Enter your email and message below."
        signal_payload = {}
        suggestions = ['Fart?', 'Ass?']

    else: 
        response = "The likely cause is that this.currentAssistantMessage does not exist as a property on your Vue instance's data object. Vue's reactivity system works on properties declared in the data function, and if a property is not defined there, it won't be reactive and may cause such errors."
        signal_payload = {}
        suggestions = ['Fart?', 'Ass?', 'Booba?']
    
    await send_assistant_response(socket_id, response, signal_payload, suggestions)


async def send_assistant_response(socket_id, response: str, signal_payload: dict, suggestions: list):
    
    from app import socketio
    
    await socketio.emit('response_started', to=socket_id)

    for word in response.split(' '):
        time.sleep(0.1)
        if stop_signals.get(socket_id): 
            stop_signals.pop(socket_id, None)
            break
        await socketio.emit('response_token', {'word': word}, to=socket_id)
    await socketio.emit('response_complete', to=socket_id)

    if signal_payload: await socketio.emit('signal', signal_payload, to=socket_id)
    await socketio.emit('suggestions', {'suggestions': suggestions}, to=socket_id)


from .multiagent.hyerarchical_multiagent import create_graph, invoke_graph
graph = create_graph()


async def get_assistant_response(socket_id, uuid, input):
    profile = mongo_get_user_profile(mongo.db[f"chats_{config.get('MODE')}"], uuid)
    llm_response = await invoke_graph(graph, uuid, profile, input, socket_id)
    response = mongo_update_user_profile(mongo.db[f"chats_{config.get('MODE')}"], uuid, llm_response['profile'])
    mongo_log_response(response)


def mongo_log_response(response):
    if 'error' in response:
        print(response['error'])
    elif 'message' in response:
        print(response['message'])


def mongo_get_x_more_messages(collection, uuid, count, skip):
    try:
        skip *= count
        pipeline = [
            {"$match": {"_id": uuid}},
            {"$project": {
                "messages_count": {"$size": "$chats.general.messages"},
                "more_messages": {
                    "$slice": [
                        "$chats.general.messages",
                        {"$max": [0, {"$subtract": [{"$size": "$chats.general.messages"}, skip + count]}]},
                        {"$min": [count, {"$subtract": [{"$size": "$chats.general.messages"}, skip]}]}
                    ]
                }
            }}
        ]

        result = list(collection.aggregate(pipeline))

        if result:
            return result[0].get("more_messages", [])
        else:
            return []
    except: 
        return []

    

def mongo_insert_chat(collection, uuid, chat_id):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$set": {
                "profile": "",
                f"chats.{chat_id}": {
                    "messages": [{'role': 'assistant', 'content': 'Welcome to **SECRAG**.<br>We make security analysis easier.'}],
            }}},
            upsert=True
        )
        if result.modified_count > 0: 
            return {"message": f"Chat '{chat_id}' added or updated for user '{uuid}'."}
        elif result.upserted_id: 
            return {"message": f"User '{uuid}' created with chat '{chat_id}'."}
        else:
            return {"message": f"Chat '{chat_id}' already exists for user '{uuid}'."}
    except Exception as e: 
        return {"error": f"Error creating chat for '{uuid}' and chat '{chat_id}': {str(e)}"}


def mongo_insert_message(collection, uuid, chat_id, role, content, widgets):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$push": {f"chats.{chat_id}.messages": {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "role": role, "content": content, "widgets": widgets}}}
        )
        if result.modified_count > 0: 
            return {"message": f"Message added to chat '{chat_id}' for user '{uuid}'."}
        else: 
            return {"error": f"Chat '{chat_id}' not found for user '{uuid}'."}
    except Exception as e:
        return {"error": f"Error inserting message for '{uuid}' and chat '{chat_id}' and message '{content}': {str(e)}"}


def mongo_get_user_profile(collection, uuid):
    try:
        user_data = collection.find_one({"_id": uuid})
        
        if user_data:
            return user_data.get("profile", "")
        else:
            return {"error": f"User with UUID '{uuid}' not found."}
    except Exception as e:
        return {"error": f"Error retrieving profile for '{uuid}': {str(e)}"}


def mongo_update_user_profile(collection, uuid, profile):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$set": {"profile": profile}}
        )
        if result.modified_count > 0: 
            return {"message": f"Profile updated for user '{uuid}'."}
        else: 
            return {"error": f"User '{uuid}' not found."}
    except Exception as e:
        return {"error": f"Error updating profile for '{uuid}': {str(e)}"}