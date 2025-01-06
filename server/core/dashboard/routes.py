from fastapi.responses import JSONResponse
from .utils import get_assistant_response, mongo_insert_chat, mongo_log_response, mongo_insert_message
from ..general.utils import log, decode_token
from ...globals import config, mongo
from fastapi import APIRouter, Request

routes = APIRouter()

@routes.post('/new-chat')
async def new_chat_post(request: Request):
    data = await request.json()
    token = data.get("token")
    chat = data.get("chat")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_insert_chat(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], chat)
    mongo_log_response(response)
    if 'error' in response: return JSONResponse(content={'error': 'Something went wrong with chat creation.'})

    log('debug', f'New chat created for {user_info["uuid"]}: {chat}')
    return JSONResponse(200)


@routes.post('/new-message')
async def new_message_post(request: Request):

    data = await request.json()
    token = data.get("token")
    role = data.get("role")
    input = data.get("input")
    socket_id = data.get("socketId")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    mongo_insert_message(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], 'general', role, input)
    if role == 'user': await get_assistant_response(socket_id, user_info['uuid'], input)
    
    return 200
