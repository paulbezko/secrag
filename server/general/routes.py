from werkzeug.security import check_password_hash, generate_password_hash
from captcha.image import ImageCaptcha
from datetime import datetime, timezone, timedelta
from .utils import get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp
from flask import Blueprint, request, current_app, jsonify, render_template_string

import random
import stripe
import base64
import io

# Routes initialization
routes = Blueprint('routes', __name__)

@routes.route('/router', methods=['GET'])
def router_get():

    try: user_info = decode_token(request.args.get('token'))
    except Exception as error: return {'error': 'Error decoding token: ' + str(error)}
    return {'authenticated': True, 'subscription': user_info.get('subscription', False), 'onboarding': user_info.get('onboarding', False)}


@routes.route('/get-user-data', methods=['GET'])
def get_user_data_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    user = get_user_data(user_info['email'])
    user_info = {
        'email': user['email'],
        'name': user['name'],
        'auth_type': user['auth_type'],
        'subscription': user['subscription'],
        'subscription_tokens_left': user['subscription_tokens_left'], #########################################################
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


@routes.route('/edit-user', methods=['POST'])
def edit_user_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}
    user = get_user_data(user_info['email'])

    if request.json.get('action') == 'changeName':
        execute_query("UPDATE users SET name = %s WHERE email = %s", (request.json.get('name'), user_info['email']))

        if user['stripe_user_id']: stripe.Customer.modify(user['stripe_user_id'], name = request.json.get('name'))
        user_info['name'] = request.json.get('name')
        token = encode_token(user_info)

        return {'token': token, 'message': 'Name change successful'}
    
    elif request.json.get('action') == 'changeEmail':

        if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'Password is not correct'}
        if get_user_data(request.json.get('password')): return {'error': 'User with this email already exists'}

        email_payload = user_info
        email_payload['action'] = 'changeEmail'
        email_payload['emailNew'] = request.json.get('emailNew')
        email_payload['expiry'] = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        token = encode_token(email_payload)
        send_email_from_template(email = request.json.get('emailNew'), template = 'changeEmail', payload = token)
        execute_query("UPDATE users SET link_token = %s WHERE email = %s", (token, user_info['email']))
        return {'message': 'Confirmation email sent'}
    
    elif request.json.get('action') == 'changePassword':

        if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'Password is not correct'}

        password_encrypted = generate_password_hash(request.json.get('passwordNew'))
        execute_query("UPDATE users SET password = %s WHERE email = %s", (password_encrypted, user_info['email']))
        return {'message': 'Password change successful'}
    
    elif request.json.get('action') == 'deleteAccount':

        if user['auth_type'] == 'password':
            if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'Password is not correct'}
        
        if user['auth_type'] != 'password': 
            if user_info['captcha_answer'] != request.json.get('captcha'): return {'error': 'Captcha is not correct'}

        if user['stripe_user_id']: stripe.Customer.delete(user['stripe_user_id'])

        execute_query("DELETE FROM users WHERE email = %s", (user_info['email'],))
        return {}


@routes.route('/change-email', methods=['GET'])
def change_email_get():

    try: email_payload = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    user = get_user_data(email_payload['email'])

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return {'error': 'linkExpired'}
    if user['link_token'] != request.args.get('token'): return {'error': 'linkExpired'}

    execute_query("UPDATE users SET email = %s, link_token = %s WHERE email = %s", (email_payload['emailNew'], None, email_payload['email']))
    if user['stripe_user_id']: stripe.Customer.modify(user['stripe_user_id'], email = email_payload['emailNew'])

    email_payload['email'] = email_payload['emailNew']
    del email_payload['emailNew']

    token = encode_token(email_payload)
    return {'token': token}


@routes.route('/get-captcha', methods=['GET'])
def get_captcha_get():

    try: user_info = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}
            
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
    return jsonify({
        'captcha_image': f"data:image/png;base64,{image_base64}",
        'token': token
    })


@routes.route('/contact', methods=['POST'])
def contact_post():

    payload = f"""
Sender name: {request.json.get('name')}
Sender email: {request.json.get('email')}
Message: {request.json.get('message')}
"""

    try: 
        send_email_from_template(email = current_app.config['MAIL_CONTACT_USER'], template = 'contact', payload = payload)
        return {}
    except: return {'error': 'Error sending message.'}


@routes.route('/get-policy', methods=['GET'])
def get_policy_get():

    policy = request.args.get('policy')

    with open(f"database/policies/{policy}.md", encoding="utf-8", mode="r") as f:
        content = f.read()

    variables = {
        "project_name": "SECRag",
        "company_name": "Manart",
        "email_support": "secrag.info@gmail.com"
    }

    return render_template_string(content, **variables)