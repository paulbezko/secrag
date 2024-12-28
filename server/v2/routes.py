from fastapi.responses import JSONResponse
from werkzeug.security import check_password_hash, generate_password_hash
from .utils import get_assistant_response, get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp, log, mongo_insert_chat, mongo_log_response, mongo_insert_message
from datetime import datetime, timezone, timedelta
from ..globals import config, mongo
from fastapi import APIRouter, Request
from jinja2 import Template

import string
import random

routes = APIRouter()

@routes.get('/init-anon-user')
async def initi_anon_user_get():

    # Generating a random 16 length token
    uuid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    # Insert user into database
    query = f"INSERT INTO users_{config.get('MODE')} (uuid, user_status) VALUES (%s, %s)"
    execute_query(query, (uuid, 'anonymous'))

    # Create chat for user
    token = encode_token({'uuid': uuid, 'user_status': 'anonymous'})
    return JSONResponse(content={'token': token})


@routes.get('/get-user-data')
def get_user_data_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})

    try:
        user = get_user_data('uuid', user_info['uuid'])
        user_info = {
            'user_status': user['user_status'],
            'uuid': user['uuid'],
            'email': user['email'],
            'name': user['name'],
            'auth_type': user['auth_type'],
            'subscription_tier': user['subscription_tier'],
            'subscription_tokens': user['subscription_tokens'],
            'stripe_subscription_id': user['stripe_subscription_id'],
            'stripe_user_id': user['stripe_user_id'],
        }

        token = encode_token(user_info)
        return {
            'token': token,
            'user_status': user_info['user_status'],
            'email': user_info['email'],
            'name': user_info['name'],
            'auth_type': user_info['auth_type'],
            'subscription_tier': user_info['subscription_tier'],
            'subscription_tokens': user_info['subscription_tokens']
            }
    
    except Exception as error:
        log('critical', 'Error retrieving user data: ' + str(error))
        return JSONResponse(content={'critical': 'Error retrieving user data: ' + str(error)})


# This route is used for email signup confirmation and password reset links
@routes.get('/process-url-token')
async def decode_url_token_get(token: str):

    try: token_info = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})
    if not check_timestamp(token_info['expiry']): return JSONResponse(content={'error': 'The link has expired.'})

    if 'action' not in token_info: return JSONResponse(content={'error': 'Invalid token.'})

    # Email confirmation
    if token_info['action'] == 'confirm_email':

        if get_user_data('email', token_info['email']): return JSONResponse(content={'error': 'This email is already verified.'})

        log('debug', f'Signup email confirmed for {token_info['email']}')
        query = f"UPDATE users_{config.get('MODE')} SET user_status = %s, auth_type = 'email', email = %s WHERE uuid = %s"
        execute_query(query, ('verified', token_info['email'], token_info['uuid']))

        return JSONResponse(content={'action': 'confirm_email', 'input_mode': 'default'})
    
    # Password reset
    elif token_info['action'] == 'reset_password':

        if not get_user_data('email', token_info['email']): return JSONResponse(content={'error': 'No user found with this email.'})
        return JSONResponse(content={'action': 'reset_password', 'input_mode': 'reset_password'})
    
    else: return JSONResponse(content={'error': 'Invalid token.'})


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

    if role == 'user': await get_assistant_response(socket_id, input)
    mongo_insert_message(mongo.db[f"chats_{config.get('MODE')}"], user_info['uuid'], 'general', role, input)

    return 200


@routes.post('/signup-email')
async def signup_email_post(request: Request):

    data = await request.json()
    token = data.get("token")
    email = data.get("email")
    socket_id = data.get("socketId")

    uuid = decode_token(token)['uuid']
    user = get_user_data('email', email)
    if user: return JSONResponse(content={'error': 'This user already exists. Try logging in instead.'})

    email_payload = {
        'action': 'confirm_email',
        'uuid': uuid,
        'email': email,
        'socket_id': socket_id,
        'expiry': (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    }

    token = encode_token(email_payload)
    send_email_from_template(email = email, template = 'signUp', payload = token)
    log('debug', f'Signup email sent to {email}')
    return JSONResponse(200)


@routes.post('/signup-password')
async def signup_password_post(request: Request):

    data = await request.json()
    token = data.get("token")
    password = data.get("password")

    uuid = decode_token(token)['uuid']
    user_info = get_user_data('uuid', uuid)
    password_encrypted = generate_password_hash(password)

    log('debug', f'Password setup confirmed for {user_info['email']}')
    query = f"UPDATE users_{config.get('MODE')} SET user_status = %s, password = %s WHERE uuid = %s"
    execute_query(query, ('registered', password_encrypted, user_info['uuid']))

    return JSONResponse(200)


@routes.post('/login')
async def login_post(request: Request):
    data = await request.json()
    token = data.get("token")
    email = data.get("email").lower()
    password = data.get("password")
    try: user = get_user_data('email', email)
    except: return JSONResponse(content={'error': '<br>Error retrieving user data'})

    if not user: return JSONResponse(content={'error': '<br>**User does not exist.** Sign up instead?'})
    if user['auth_type'] != 'email': return JSONResponse(content={'error': '<br>The authentication method is not correct. Try using another one.'})
    if not check_password_hash(user['password'], password): return JSONResponse(content={'error': '<br>**Incorrect password.** Try again.'})

    user_info = {
        'uuid': user['uuid'],
        'user_status': user['user_status'],
        'email': user['email'],
        'name': user['name'],
        'auth_type': user['auth_type'],
        'subscription_tier': user['subscription_tier'],
        'subscription_tokens': user['subscription_tokens'],
    }

    token = encode_token(user_info)
    return JSONResponse(content={'token': token, 'user_status': user_info['user_status']})


@routes.post('/authenticate-with-supabase')
async def authenticate_post(request: Request):

    data = await request.json()
    token = data.get("token")
    email = data.get("email")
    name = data.get("name")
    supabase_user_id = data.get("id")
    auth_type = data.get("auth_type")

    user_info = decode_token(token)
    user = get_user_data('email', email.lower())
    if not user:
        log('info', f'New user joined through Google: {email.lower()}')
        query = f"UPDATE users_{config.get('MODE')} SET user_status = 'registered', email = %s, name = %s, auth_type = %s, supabase_user_id = %s WHERE uuid = %s"
        execute_query(query, (email.lower(), name, auth_type, supabase_user_id, user_info['uuid']))
        user_info = {
            'uuid': user_info['uuid'],
            'user_status': 'registered',
            'email': email.lower(),
            'name': name,
            'auth_type': 'google',
        }

    elif user['auth_type'] == 'google': 
        user_info = {
            'uuid': user['uuid'],
            'user_status': user['user_status'],
            'email': email.lower(),
            'name': user['name'],
            'auth_type': user['auth_type'],
            'subscription_tier': user['subscription_tier'],
            'subscription_tokens': user['subscription_tokens'],
        }

    else: return JSONResponse(content={'error': '<br>The authentication method is not correct. Try using another one.'})
    token = encode_token(user_info)
    return JSONResponse(content={'token': token, 'user_status': user_info['user_status']})


@routes.post('/forgot-password')
async def forgot_password_post(request: Request):

    data = await request.json()
    email = data.get("email").lower()
    socket_id = data.get("socketId")

    user = get_user_data('email', email)
    if not user: return JSONResponse(content={'error': '<br>No user found with this email.'})

    email_payload = {
        'action': 'reset_password',
        'uuid': user['uuid'],
        'email': email,
        'socket_id': socket_id,
        'expiry': (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    }

    token = encode_token(email_payload)
    send_email_from_template(email = email, template = 'resetPassword', payload = token)
    log('debug', f'Signup email sent to {email}')
    return JSONResponse(200)


@routes.post('/reset-password')
async def reset_password_post(request: Request):

    data = await request.json()
    token = data.get("token")
    password = data.get("password")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token.'})

    print(user_info)

    password_encrypted = generate_password_hash(password)

    log('debug', f'Password reset confirmed for {user_info['email']}')
    query = f"UPDATE users_{config.get('MODE')} SET password = %s WHERE uuid = %s"
    execute_query(query, (password_encrypted, user_info['uuid']))

    return JSONResponse(200)


@routes.get('/get-policy')
def get_policy_get(policy: str):

    with open(f"database/policies/{policy}.md", encoding="utf-8", mode="r") as f:
        content = f.read()

    variables = {
        "project_name": "SECRAG",
        "company_name": "Manart",
        "email_support": "contact@secrag.com"
    }

    return Template(content).render(variables)