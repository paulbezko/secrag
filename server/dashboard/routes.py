from .utils.miscellaneous import save_message, get_user_ip
from .utils.vectorstore import vectorstore_manager
from ..general.utils import encode_token, decode_token, execute_query, log
from .utils.secedgar import get_filing
from .utils.llm import get_assistant_response
from .utils.mongo import mongo_insert_message, mongo_get_messages_by_chat, mongo_get_chats_by_user_id, mongo_insert_chat, mongo_reset_chat, mongo_delete_chat, mongo_log_response
from ..lib_secrag.edgar.entities import get_entity
from ..globals import config, mongo
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

routes = APIRouter()

@routes.get('/get-chats')
def get_chats_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_get_chats_by_user_id(mongo.collection_messages_authenticated, user_info['email'])
    if 'error' in response:
        mongo_log_response(response)
        return JSONResponse(content={'error': 'Something went wrong with chat retrieval.'})

    return JSONResponse(content={'chats': response})


@routes.get('/get-messages')
def get_messages_get(chat: str, token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_get_messages_by_chat(mongo.collection_messages_authenticated, user_info['email'], chat)
    if 'error' in response:
        mongo_log_response(response)
        return JSONResponse(content={'error': 'Something went wrong with message retrieval.'})

    return JSONResponse(content=response)


@routes.post('/new-chat')
async def new_chat_post(request: Request):
    data = await request.json()
    token = data.get("token")
    chat = data.get("chat")
    socket_id = data.get("socketId")
    filing_date = data.get("filingDate")
    cik = data.get("cik")

    from app import socketio
    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    token_cost_chat = 0
    if int(user_info['subscription_tokens_left']) < token_cost_chat: return JSONResponse(content={'error': 'Insufficient Tokens'})

    socket_id = socket_id
    await socketio.emit('new_chat_started', to=socket_id)

    await socketio.emit('new_chat_initialized', to=socket_id)
    filing = get_filing(filing_id=chat, filing_date=filing_date, filing_cik=cik)
    await socketio.emit('new_chat_downloaded', to=socket_id)
    try:
        await vectorstore_manager.new_chat(filing)
    except Exception as e:
        return JSONResponse(content={'error': "Unparsable filing"})
    await socketio.emit('new_chat_vectorized', to=socket_id)

    response = mongo_insert_chat(mongo.collection_messages_authenticated, user_info['email'], user_info['name'], chat, filing_date)
    mongo_log_response(response)
    if 'error' in response: return JSONResponse(content={'error': 'Something went wrong with chat creation.'})

    log('debug', f'New chat created for {user_info["email"]}: {chat}')
    query = f"UPDATE users_{config.get('MODE')} SET subscription_tokens_left = %s WHERE email = %s"
    execute_query(query, (int(user_info['subscription_tokens_left']) - token_cost_chat, user_info['email']))

    user_info['subscription_tokens_left'] = int(user_info['subscription_tokens_left']) - token_cost_chat
    token = encode_token(user_info)

    return JSONResponse(content={'token': token})


@routes.post('/new-chat-preview')
async def new_chat_preview_post(request: Request):
    data = await request.json()
    chat = data.get("chat")
    socket_id = data.get("socketId")
    filing_date = data.get("filingDate")
    cik = data.get("cik")

    user_ip = get_user_ip(request)

    from app import socketio
    socket_id = socket_id
    await socketio.emit('new_chat_started', to=socket_id)
    
    await socketio.emit('new_chat_initialized', to=socket_id)
    filing = get_filing(filing_id=chat, filing_date=filing_date, filing_cik=cik)
    await socketio.emit('new_chat_downloaded', to=socket_id)
    try:
        await vectorstore_manager.new_chat(filing)
    except:
        return JSONResponse(content={'error': "Unparsable filing"})    
    await socketio.emit('new_chat_vectorized', to=socket_id)

    response = mongo_insert_chat(mongo.collection_messages_anonymous, user_ip, None, chat, filing_date)
    mongo_log_response(response)
    if 'error' in response: return JSONResponse(content={'error': 'Something went wrong with chat creation.'})

    return JSONResponse(content={'success': True})


@routes.get('/get-filing-selection-data')
def get_filing_selection_data_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    with open('database/memory/filings_available.json', 'r') as f: filings_available = json.load(f)
    with open('database/memory/filings_new.json', 'r') as f: filings_new = json.load(f)

    return JSONResponse(content={'filingKeys': list(filings_available.keys()), 'newFilings': filings_new})


@routes.get('/get-info-by-ticker')
def get_info_by_ticker_get(token: str, ticker: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    with open('database/memory/filings_available.json', 'r') as f: filings_available = json.load(f)

    return JSONResponse(content={'info': filings_available[ticker]})


@routes.get('/get-info-by-ticker-preview')
def get_info_by_ticker_preview_get(ticker: str):

    with open('database/memory/filings_preview.json', 'r') as f: filings_available = json.load(f)
    return JSONResponse(content={'info': filings_available[ticker]})


@routes.get('/get-filing')
async def get_filing_get(token: str, chat: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_get_messages_by_chat(mongo.collection_messages_authenticated, user_info['email'], chat)
    if 'error' in response:
        mongo_log_response(response)
        return JSONResponse(content={'error': 'Something went wrong with filing retrieval.'})

    ticker, year, form_raw = chat.split('-')
    filing_date = response['filing_date']

    if form_raw == '10K': form = '10-K'
    elif '10Q' in form_raw: form = '10-Q'

    try: 
        with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'r') as f: html = f.read()
        return JSONResponse(content={'html': html})
    
    except:
        try:
            entity = await get_entity(ticker)
            html = entity.get_filings(form=form, date=filing_date)[0].html()

            with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'w') as f: f.write(html)
            return JSONResponse(content={'html': html})
        
        except Exception as error:
            return JSONResponse(content={'error': 'Error getting filing: ' + str(error)})


@routes.get('/get-filing-preview')
async def get_filing_preview_get(chat: str, filingDate: str):

    ticker, year, form_raw = chat.split('-')
    filing_date = filingDate
    if form_raw == '10K': form = '10-K'
    elif '10Q' in form_raw: form = '10-Q'

    try: 
        with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'r') as f: html = f.read()
        return JSONResponse(content={'html': html})
    
    except:
        try:
            entity = await get_entity(ticker)
            html = entity.get_filings(form=form, date=filing_date)[0].html()

            with open(f'database/filings/{ticker.upper()}-{year}-{form_raw}.html', 'w') as f: f.write(html)
            return JSONResponse(content={'html': html})
        
        except Exception as error:
            return JSONResponse(content={'error': 'Error getting filing: ' + str(error)})


@routes.post('/reset-chat')
async def reset_chat_post(request: Request):
    data = await request.json()
    chat = data.get("chat")
    token = data.get("token")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_reset_chat(mongo.collection_messages_authenticated, user_info['email'], chat)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with chat reset.'})

    return JSONResponse(content={'success': True})


@routes.post('/delete-chat')
async def delete_chat_post(request: Request):
    data = await request.json()
    chat = data.get("chat")
    token = data.get("token")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_delete_chat(mongo.collection_messages_authenticated, user_info['email'], chat)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with chat deletion.'})

    return JSONResponse(content={'success': True})


@routes.post('/new-message-user')
async def new_message_user_post(request: Request):
    data = await request.json()
    message = data.get("message")
    chat = data.get("chat")
    last_x_messages = data.get("lastXMessages")
    socket_id = data.get("socketId")
    filing_date = data.get("filingDate")
    token = data.get("token")

    from app import socketio
    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    token_cost_message = 1
    if int(user_info['subscription_tokens_left']) < token_cost_message: return JSONResponse(content={'error': 'Insufficient Tokens'})

    message_history = (last_x_messages)

    response = mongo_insert_message(mongo.collection_messages_authenticated, user_info["email"], chat, 'user', message)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with message insertion.'})

    await get_assistant_response(
        user_prompt = message,
        message_history = message_history,
        filing_id = chat,
        socket_id = socket_id,
        filing_date = filing_date,
        socketio_handler=socketio
    )

    query = f"UPDATE users_{config.get('MODE')} SET subscription_tokens_left = %s WHERE email = %s"
    execute_query(query, (int(user_info['subscription_tokens_left']) - token_cost_message, user_info['email']))

    user_info['subscription_tokens_left'] = int(user_info['subscription_tokens_left']) - token_cost_message
    token = encode_token(user_info)
    return JSONResponse(content={'token': token})


@routes.post('/new-message-user-preview')
async def new_message_user_preview_post(request: Request):
    data = await request.json()
    message = data.get("message")
    chat = data.get("chat")
    last_x_messages = data.get("lastXMessages")
    socket_id = data.get("socketId")
    filing_date = data.get("filingDate")
    token = data.get("token")

    user_ip = get_user_ip(request)

    from app import socketio
    message_history = (last_x_messages)

    response = mongo_insert_message(mongo.collection_messages_anonymous, user_ip, chat, 'user', message)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with message insertion.'})

    await get_assistant_response(
        user_prompt = message,
        message_history = message_history,
        filing_id = chat,
        socket_id = socket_id,
        filing_date = filing_date,
        socketio_handler=socketio
    )

    return JSONResponse(content={'success': True})


@routes.post('/new-message-assistant')
async def new_message_assistant_post(request: Request):
    data = await request.json()
    message = data.get("message")
    chat = data.get("chat")
    token = data.get("token")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    response = mongo_insert_message(mongo.collection_messages_authenticated, user_info["email"], chat, 'assistant', message)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with message insertion.'})

    return JSONResponse(content={'success': True})


@routes.post('/new-message-assistant-preview')
async def new_message_assistant_preview_post(request: Request):
    data = await request.json()
    message = data.get("message")
    chat = data.get("chat")

    user_ip = get_user_ip(request)

    response = mongo_insert_message(mongo.collection_messages_anonymous, user_ip, chat, 'assistant', message)
    mongo_log_response(response)
    if 'error' in response:
        return JSONResponse(content={'error': 'Something went wrong with message insertion.'})

    return JSONResponse(content={'success': True})







from werkzeug.security import check_password_hash, generate_password_hash
from ..general.utils import encode_token, get_user_data
from ..globals import stop_signals
from fastapi import APIRouter, Request
import time
import re

# routes = APIRouter()

async def get_assistant_response_v2(socket_id, input):
    if input == "I'd like to sign up.":
        response = "Sure! Enter your email below to start."
        signal_payload = {'signal_type': 'sign_up'}
        suggestions = []
    
    elif input == "I'd like to sign in.":
        response = "Of course! Enter your email and password below."
        signal_payload = {'signal_type': 'sign_in'}
        suggestions = ['I forgot my password']

    elif input == "I forgot my password":
        response = "No worries. Enter your email below and we'll send you a reset link."
        signal_payload = {'signal_type': 'reset_password'}
        suggestions = ['Assi?']

    elif input == "I'd like to know more about the pricing.":
        response = "Sure! Here's the pricing plan."
        signal_payload = {}
        suggestions = ['Ass?']
    
    elif input == "I'd like to contact you.":
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
    if suggestions: await socketio.emit('suggestions', {'suggestions': suggestions}, to=socket_id)


@routes.post('/test-new-message')
async def test_new_message_post(request: Request):

    data = await request.json()
    input = data.get("input")
    socket_id = data.get("socketId")
    await get_assistant_response_v2(socket_id, input)

    return 200



@routes.post('/test-authenticate')
async def test_authenticate_post(request: Request):

    data = await request.json()
    type = data.get("type")
    socket_id = data.get("socketId")

    if type == 'sign_up':
        
        email = data.get("email")

        if not re.match(r'^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$', email): response = "Please enter a valid email address."
        # Add a check where user exists already
        else: response, signal_payload = "An email with a sign up link has been sent to you.", {}
            # Action to send email



        data = await request.json()
        token = data.get("token")
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")
        # Determining if the user has clicked the email link or not
        if token:
            try: 
                user_info = decode_token(token)
                stage = 'SignUpAfter'
            except: return JSONResponse(content={'error': 'Error decoding token'})
        else:
            stage = 'SignUpBefore'
            email = email.lower()

            # The user has not requested an email yet
            if stage == 'SignUpBefore':

                user = get_user_data(email.lower())
                if user: return JSONResponse(content={'error': 'User with this email already exists'})

                email_payload = {
                    'email': email,
                    'action': 'signUp',
                    'expiry': (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                }

                token = encode_token(email_payload)
                send_email_from_template(email = email, template = 'signUp', payload = token)
                log('debug', f'Signup email sent to {email}')
                return JSONResponse(content={'message': 'Confirmation email sent'})





    elif type == 'sign_in':

        email = data.get("email")
        password = data.get("password")

        if not re.match(r'^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$', email): response = "Please enter a valid email address."

        try: 
            user = get_user_data(email.lower())

            if not user: response, signal_payload, suggestions = "User was not found. Perhaps you would like to sign up?", {}
            elif user['auth_type'] != 'password': response, signal_payload = "Looks like you signed up with another authentication method. Please sign in with that method.", {}
            elif not check_password_hash(user['password'], password): response, signal_payload = "Looks like the password is not correct. Please try again.", {}
            else:
                user_info = {
                    'email': user['email'],
                    'name': user['name'],
                    'auth_type': user['auth_type'],
                    'subscription': user['subscription'],
                    'subscription_tokens_left': user['subscription_tokens_left'],
                    'stripe_subscription_id': user['stripe_subscription_id'],
                    'stripe_user_id': user['stripe_user_id'],
                }

                token = encode_token(user_info)
                response, signal_payload = "Welcome back!", {'signal_type': 'signed_in', 'token': token, 'subscription': user['subscription']}

        except: response, signal_payload = "Something went wrong with authentication.", {}

    elif type == 'reset_password':
        
        email = data.get("email")

        if not re.match(r'^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$', email): response = "Please enter a valid email address."
        else: response = "A password reset link has been sent to you."
            # Action to send email

    else: response = "Something went wrong."

    await send_assistant_response(socket_id, response, signal_payload, None)

@routes.get('/test-get-user-data')
async def test_get_user_data_get(token: str):
    uuid = decode_token(token)['uuid']
    user = get_user_data(uuid)
    return JSONResponse(content={'userStatus': user['status']})