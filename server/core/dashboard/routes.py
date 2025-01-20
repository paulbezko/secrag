from fastapi.responses import JSONResponse
from .utils import (
    get_assistant_response, 
    mongo_get_x_more_messages,
    mongo_insert_chat, 
    mongo_log_response, 
    mongo_insert_message, 
    mongo_get_user_profile, 
    mongo_update_user_profile)
from ..general.utils import log, decode_token
from ...globals import config, mongo
from fastapi import APIRouter, Request

routes = APIRouter()


@routes.get('/get-x-more-messages')
async def get_x_more_messages_get(token: str, count: int, skip: int):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    x_more_messages = mongo_get_x_more_messages(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], count, skip)

    return JSONResponse(content={'x_more_messages': x_more_messages})


@routes.get('/get-user-profile')
async def get_user_profile_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    profile = mongo_get_user_profile(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'])

    return JSONResponse(content={'profile': profile})


@routes.post('/update-user-profile')
async def update_user_profile_get(request: Request):
    data = await request.json()
    token = data.get("token")
    profile = data.get("profile")
    
    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    profile = mongo_update_user_profile(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], profile)

    return JSONResponse(content={'profile': profile})


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
    widgets = data.get("widgets")
    socket_id = data.get("socketId")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    mongo_insert_message(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], 'general', role, input, widgets)
    if role == 'user': await get_assistant_response(socket_id, user_info['uuid'], input)
    
    return 200
