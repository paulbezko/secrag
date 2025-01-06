from ...globals import stop_signals

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
    
    response = await invoke_graph(graph, uuid, input, socket_id, debug=False)
    print(response)

def mongo_log_response(response):
    if 'error' in response:
        print(response['error'])
    elif 'message' in response:
        print(response['message'])


def mongo_insert_chat(collection, uuid, chat_id):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$set": {f"chats.{chat_id}": {
                "messages": []
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


def mongo_insert_message(collection, uuid, chat_id, role, content):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$push": {f"chats.{chat_id}.messages": {"role": role, "content": content}}}
        )
        if result.modified_count > 0: 
            return {"message": f"Message added to chat '{chat_id}' for user '{uuid}'."}
        else: 
            return {"error": f"Chat '{chat_id}' not found for user '{uuid}'."}
    except Exception as e:
        return {"error": f"Error inserting message for '{uuid}' and chat '{chat_id}' and message '{content}': {str(e)}"}
