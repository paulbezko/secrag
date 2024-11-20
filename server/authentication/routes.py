from fastapi.responses import JSONResponse
from werkzeug.security import check_password_hash, generate_password_hash
from ..general.utils import get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp, log
from datetime import datetime, timezone, timedelta
from ..globals import config
from fastapi import APIRouter, Request

routes = APIRouter()


@routes.post('/signup')
async def signup_post(request: Request):

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


    # The user came after clicking the email link
    if stage == 'SignUpAfter':

        password_encrypted = generate_password_hash(password)

        log('debug', f'User account created for {user_info['email']}')
        log('info', f'New user joined through email: {user_info['email']}')
        query = f"UPDATE users_{config.get('MODE')} SET name = %s, auth_type = 'password', password = %s WHERE email = %s"
        execute_query(query, (name, password_encrypted, user_info['email']))

        user_info['name'] = name
        user_info['subscription'] = 'none'
        del user_info['onboarding']

        token = encode_token(user_info)
        return JSONResponse(content={'token': token})



@routes.get('/signup')
def signup_get(token: str):

    try: email_payload = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return JSONResponse(content={'error': 'linkExpired'})
    if get_user_data(email_payload['email']): return JSONResponse(content={'critical': 'userExists'})

    log('debug', f'Signup email confirmed for {email_payload['email']}')
    query = f"INSERT INTO users_{config.get('MODE')} (email) VALUES (%s)"
    execute_query(query, (email_payload['email'],))

    user_info = email_payload
    user_info['onboarding'] = True

    token = encode_token(user_info)
    return JSONResponse(content={'token': token})


@routes.post('/login')
async def login_post(request: Request):
    data = await request.json()
    token = data.get("token")
    email = data.get("email")
    password = data.get("password")

    try: user = get_user_data(email.lower())
    except: return JSONResponse(content={'error': 'Error retrieving user data'})

    if not user: return JSONResponse(content={'error': 'userNotFound'})
    if user['auth_type'] != 'password': return JSONResponse(content={'error': 'authMethodIncorrect'})
    if not check_password_hash(user['password'], password): return JSONResponse(content={'error': 'invalidCredentials'})

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
    return JSONResponse(content={'token': token})


@routes.post('/reset-password')
async def reset_password_post(request: Request):
    
    data = await request.json()
    token = data.get("token")
    action = data.get("action")
    email = data.get("email")
    password = data.get("password")

    if action == 'resetPasswordBefore':

        user = get_user_data(email.lower())
        if not user: return JSONResponse(content={'error': 'User does not exist'})

        email_payload = {
            'email': email.lower(),
            'action': 'resetPasswordAfter',
            'expiry': (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }

        token = encode_token(email_payload)
        send_email_from_template(email = email.lower(), template = 'resetPassword', payload = token)
        query = f"UPDATE users_{config.get('MODE')} SET link_token = %s WHERE email = %s"
        execute_query(query, (token, email.lower()))
        return JSONResponse(content={'message': 'Confirmation email sent'})
    
    elif action == 'resetPasswordAfter':

        try: user_info = decode_token(token)
        except: return JSONResponse(content={'error': 'Error decoding token'})

        password_encrypted = generate_password_hash(password)
        query = f"UPDATE users_{config.get('MODE')} SET password = %s, WHERE email = %s"
        execute_query(f"UPDATE users_{config.get('MODE')} SET password = %s WHERE email = %s", (password_encrypted, user_info['email']))

        return JSONResponse(content={'message': 'Password reset successful'})
    

@routes.get('/reset-password')
def reset_password_get(token: str):


    try: email_payload = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return JSONResponse(content={'error': 'linkExpired'})

    user = get_user_data(email_payload['email'].lower())
    if not user: return JSONResponse(content={'error': 'User does not exist'})
    if user['link_token'] != token: return JSONResponse(content={'error': 'linkExpired'})

    query = f"UPDATE users_{config.get('MODE')} SET link_token = %s WHERE email = %s"
    execute_query(query, (None, email_payload['email'].lower()))

    return {}


@routes.post('/authenticate')
async def authenticate_post(request: Request):

    data = await request.json()
    token = data.get("token")
    email = data.get("email")
    name = data.get("name")

    user = get_user_data(email.lower())
    if not user:
        log('info', f'New user joined through Google: {email.lower()}')
        query = f"INSERT INTO users_{config.get('MODE')} (email, name, auth_type, supabase_user_id) VALUES (%s, %s, %s, %s)"
        execute_query(query, (email.lower(), name, request.json.get('auth_type'), id))
        user_info = {
            'email': email.lower(),
            'name': name,
            'auth_type': 'google',
        }

    elif user['auth_type'] == 'google': 
        user_info = {
            'email': email.lower(),
            'name': user['name'],
            'auth_type': user['auth_type'],
            'subscription': user['subscription'],
            'subscription_tokens_left': user['subscription_tokens_left'],
            'stripe_subscription_id': user['stripe_subscription_id'],
            'stripe_user_id': user['stripe_user_id'],
        }
    else: return JSONResponse(content={'error': 'authMethodIncorrect'})

    token = encode_token(user_info)
    return JSONResponse(content={'token': token})