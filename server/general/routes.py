from fastapi.responses import JSONResponse
from jinja2 import Template
from werkzeug.security import check_password_hash, generate_password_hash
from captcha.image import ImageCaptcha
from datetime import datetime, timezone, timedelta
from .utils import get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp, log
from ..globals import config
import traceback

import random
import stripe
import base64
import io

from fastapi import APIRouter, Request

routes = APIRouter()


@routes.get('/router')
def router_get(token: str):

    try: 
        user_info = decode_token(token)
        return JSONResponse(content={'authenticated': True, 'subscription': user_info.get('subscription', False), 'onboarding': user_info.get('onboarding', False)})
    except Exception as error: 
        return JSONResponse(content={'critical': 'Error decoding token: ' + str(error)})
    


@routes.get('/get-user-data')
def get_user_data_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})

    try:
        user = get_user_data(user_info['email'])
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
        return {
            'token': token,
            'email': user_info['email'],
            'name': user_info['name'],
            'auth_type': user_info['auth_type'],
            'subscription': user_info['subscription'],
            'subscription_tokens_left': user['subscription_tokens_left']
            }
    
    except Exception as error:
        log('critical', 'Error retrieving user data: ' + str(error))
        return JSONResponse(content={'critical': 'Error retrieving user data: ' + str(error)})


@routes.post('/edit-user')
async def edit_user_post(request: Request):
    data = await request.json()
    name = data.get("name")
    token = data.get("token")
    action = data.get("action")
    password = data.get("password")
    email_new = data.get("emailNew")
    password_new = data.get("passwordNew")
    captcha = data.get("captcha")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})

    try:
        user = get_user_data(user_info['email'])

        if action == 'changeName':
            query = f"UPDATE users_{config.get('MODE')} SET name = %s WHERE email = %s"
            execute_query(query, (name, user_info['email']))
            
            if user['stripe_user_id']: stripe.Customer.modify(user['stripe_user_id'], name = name)
            user_info['name'] = name
            token = encode_token(user_info)

            return JSONResponse(content={'token': token, 'message': 'Name change successful'})
        
        elif action == 'changeEmail':

            if not check_password_hash(user['password'], password): return JSONResponse(content={'error': 'Password is not correct'})
            if get_user_data(password): return JSONResponse(content={'error': 'User with this email already exists'})

            email_payload = user_info
            email_payload['action'] = 'changeEmail'
            email_payload['emailNew'] = email_new
            email_payload['expiry'] = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

            token = encode_token(email_payload)
            send_email_from_template(email = email_new, template = 'changeEmail', payload = token)

            query = f"UPDATE users_{config.get('MODE')} SET link_token = %s WHERE email = %s"
            execute_query(query, (token, user_info['email']))
            return JSONResponse(content={'message': 'Confirmation email sent'})
        
        elif action == 'changePassword':

            if not check_password_hash(user['password'], password): return JSONResponse(content={'error': 'Password is not correct'})

            password_encrypted = generate_password_hash(password_new)

            query = f"UPDATE users_{config.get('MODE')} SET password = %s WHERE email = %s"
            execute_query(query, (password_encrypted, user_info['email']))
            return JSONResponse(content={'message': 'Password change successful'})
        
        elif action == 'deleteAccount':

            if user['auth_type'] == 'password':
                if not check_password_hash(user['password'], password): return JSONResponse(content={'error': 'Password is not correct'})
            
            if user['auth_type'] != 'password': 
                if user_info['captcha_answer'] != captcha: return JSONResponse(content={'error': 'Captcha is not correct'})

            if user['stripe_user_id']: stripe.Customer.delete(user['stripe_user_id'])

            query = f"DELETE FROM users_{config.get('MODE')} WHERE email = %s"
            execute_query(query, (user_info['email'],))
            return {}

    except Exception as error:
        log('critical', traceback.format_exc())
        log('critical', 'Error editing user data: ' + str(error))
        return JSONResponse(content={'critical': 'Error editing user data: ' + str(error)})


@routes.get('/change-email')
async def change_email_get(token: str):

    try: email_payload = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})

    user = get_user_data(email_payload['email'])

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return JSONResponse(content={'error': 'linkExpired'})
    if user['link_token'] != token: return JSONResponse(content={'error': 'linkExpired'})

    query = f"UPDATE users_{config.get('MODE')} SET email = %s, link_token = %s WHERE email = %s"
    execute_query(query, (email_payload['emailNew'], None, email_payload['email']))
    if user['stripe_user_id']: stripe.Customer.modify(user['stripe_user_id'], email = email_payload['emailNew'])

    email_payload['email'] = email_payload['emailNew']
    del email_payload['emailNew']

    token = encode_token(email_payload)
    return JSONResponse(content={'token': token})


@routes.get('/get-captcha')
async def get_captcha_get(token: str):

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'critical': 'Error decoding token'})
            
    captcha_question = str(random.randint(100, 999))
    image = ImageCaptcha(width = 170, height = 100)
    data = image.generate(captcha_question)

    # Save the image to a BytesIO stream
    image_data = io.BytesIO()
    image.write(captcha_question, image_data)
    image_data.seek(0)

    # Encode the image in base64 to send as JSON
    image_base64 = base64.b64encode(image_data.getvalue()).decode('utf-8')

    user_info['captcha_answer'] = captcha_question
    token = encode_token(user_info)

    # Send the image and the encrypted answer as JSON
    return JSONResponse(content={
        'captcha_image': f"data:image/png;base64,{image_base64}",
        'token': token
    })


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