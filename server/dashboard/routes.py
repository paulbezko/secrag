import asyncio
from .utils.miscellaneous import save_message
from .utils.vectorstore import vectorstore_manager
from ..general.utils import encode_token, decode_token, execute_query, log
from .utils.secedgar import get_filing
from .utils.llm import get_assistant_response
from flask import request, Blueprint, current_app
from edgar import *
from .. import socketio

import json

# Routes initialization
routes = Blueprint('routes', __name__)

@routes.route('/get-chats', methods=['GET'])
def get_chats_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)
    if user_info['email'] in memory:
        chats = list(reversed(memory[user_info['email']].keys()))
    else:
        chats = []
    return {'chats': chats}


@routes.route('/get-messages', methods=['GET'])
def get_messages_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)
    messages = memory[user_info['email']][request.args.get('chat')]['messages']
    filing_date = memory[user_info['email']][request.args.get('chat')]['filing_date']
    return {'messages': messages, 'filing_date': filing_date}


@routes.route('/new-chat', methods=['POST'])
def new_chat_post():
    
    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    token_cost_chat = 20
    if int(user_info['subscription_tokens_left']) < token_cost_chat: return {'error': 'Insufficient Tokens'}

    socket_id = request.json.get('socketId')
    socketio.emit('new_chat_started', to=socket_id)

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)
    if user_info['email'] not in memory: memory[user_info['email']] = {}
    memory[user_info['email']][request.json.get('chat')] = {'filing_date': request.json.get('filingDate'), 'messages': [{'role': 'assistant', 'content': f'Hello {user_info["name"]}! {request.json.get('chat')} is embedded and ready for discussion. How can I help you today?'}]}
    with open('database/memory/chats.json', 'w') as f: json.dump(memory, f, indent=2)
    
    socketio.emit('new_chat_initialized', to=socket_id)
    filing = get_filing(filing_id=request.json.get('chat'), filing_date=request.json.get('filingDate'))
    socketio.emit('new_chat_downloaded', to=socket_id)
    vectorstore_manager.new_chat(filing)
    socketio.emit('new_chat_vectorized', to=socket_id)

    log('debug', f'New chat created for {user_info["email"]}: {request.json.get("chat")}')
    query = f"UPDATE users_{current_app.config['MODE']} SET subscription_tokens_left = %s WHERE email = %s"
    execute_query(query, (int(user_info['subscription_tokens_left']) - token_cost_chat, user_info['email']))

    user_info['subscription_tokens_left'] = int(user_info['subscription_tokens_left']) - token_cost_chat
    token = encode_token(user_info)

    return {'token': token}


@routes.route('/new-chat-preview', methods=['POST'])
def new_chat_preview_post():

    socket_id = request.json.get('socketId')
    socketio.emit('new_chat_started', to=socket_id)
    
    socketio.emit('new_chat_initialized', to=socket_id)
    filing = get_filing(filing_id=request.json.get('chat'), filing_date=request.json.get('filingDate'))
    socketio.emit('new_chat_downloaded', to=socket_id)
    vectorstore_manager.new_chat(filing)
    socketio.emit('new_chat_vectorized', to=socket_id)

    return {'success': True}


@routes.route('/get-filing-selection-data', methods=['GET'])
def get_list_tickers_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/filings_available.json', 'r') as f: filings_available = json.load(f)
    with open('database/memory/filings_new.json', 'r') as f: filings_new = json.load(f)

    return {'tickers': list(filings_available.keys()), 'newFilings': filings_new}


@routes.route('/get-info-by-ticker', methods=['GET'])
def get_info_by_ticker_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/filings_available.json', 'r') as f: filings_available = json.load(f)

    return {'info': filings_available[request.args.get('ticker')]}


@routes.route('/get-info-by-ticker-preview', methods=['GET'])
def get_info_by_ticker_preview_get():

    with open('database/memory/filings_preview.json', 'r') as f: filings_available = json.load(f)
    return {'info': filings_available[request.args.get('ticker')]}


@routes.route('/get-filing', methods=['GET'])
def get_filing_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)

    ticker, year, form_raw = request.args.get('chat').split('-')
    filing_date = memory[user_info['email']][request.args.get('chat')]['filing_date']
    if form_raw == '10K': form = '10-K'
    elif '10Q' in form_raw: form = '10-Q'

    try: 
        with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'r') as f: html = f.read()
        return {'html': html}
    
    except:
        try:
            html = Company(ticker).get_filings(form=form, date=filing_date)[0].html()

            with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'w') as f: f.write(html)
            return {'html': html}
        
        except Exception as error:
            return {'error': 'Error getting filing: ' + str(error)}


@routes.route('/get-filing-preview', methods=['GET'])
def get_filing_preview_get():

    ticker, year, form_raw = request.args.get('chat').split('-')
    filing_date = request.args.get('filingDate')
    if form_raw == '10K': form = '10-K'
    elif '10Q' in form_raw: form = '10-Q'

    try: 
        with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'r') as f: html = f.read()
        return {'html': html}
    
    except:
        try:
            html = Company(ticker).get_filings(form=form, date=filing_date)[0].html()

            with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'w') as f: f.write(html)
            return {'html': html}
        
        except Exception as error:
            return {'error': 'Error getting filing: ' + str(error)}


@routes.route('/reset-chat', methods=['POST'])
def reset_chat_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)
    memory[user_info['email']][request.json.get('chat')]['messages'] = [{'role': 'assistant', 'content': f'Hello {user_info["name"]}! {request.json.get('chat')} is embedded and ready for discussion. How can I help you today?'}]
    with open('database/memory/chats.json', 'w') as f: json.dump(memory, f, indent=2)

    return {'success': True}


@routes.route('/delete-chat', methods=['POST'])
def delete_chat_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    with open('database/memory/chats.json', 'r') as f: memory = json.load(f)
    del memory[user_info['email']][request.json.get('chat')]
    with open('database/memory/chats.json', 'w') as f: json.dump(memory, f, indent=2)

    return {'success': True}


@routes.route('/new-message-user', methods=['POST'])
async def new_message_user_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    token_cost_message = 4
    if int(user_info['subscription_tokens_left']) < token_cost_message: return {'error': 'Insufficient Tokens'}

    message_history = (request.json.get('lastXMessages'))
    # message_history_json = [message['content'] for message in message_history_json if 'content' in message]
    save_message(email = user_info["email"], chat = request.json.get('chat'), role = 'user', message = request.json.get('message'))

    await get_assistant_response(
        user_prompt = request.json.get('message'),
        message_history = message_history,
        filing_id = request.json.get('chat'),
        socket_id = request.json.get('socketId'),
        filing_date = request.json.get('filingDate')
    )

    query = f"UPDATE users_{current_app.config['MODE']} SET subscription_tokens_left = %s WHERE email = %s"
    execute_query(query, (int(user_info['subscription_tokens_left']) - token_cost_message, user_info['email']))

    user_info['subscription_tokens_left'] = int(user_info['subscription_tokens_left']) - token_cost_message
    token = encode_token(user_info)
    return {'token': token}


@routes.route('/new-message-user-preview', methods=['POST'])
async def new_message_user_preview_post():

    message_history = (request.json.get('lastXMessages'))

    await get_assistant_response(
        user_prompt = request.json.get('message'),
        message_history = message_history,
        filing_id = request.json.get('chat'),
        socket_id = request.json.get('socketId'),
        filing_date = request.json.get('filingDate')
    )

    return {'success': True}


@routes.route('/new-message-assistant', methods=['POST'])
def new_message_assistant_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    save_message(email = user_info["email"], chat = request.json.get('chat'), role = 'assistant', message = request.json.get('message'))
    return {'success': True}


