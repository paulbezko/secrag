from werkzeug.security import check_password_hash, generate_password_hash
from captcha.image import ImageCaptcha
from datetime import datetime, timezone, timedelta
from .utils import get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp
from flask import Blueprint, render_template, send_from_directory, request, current_app, jsonify

import supabase
import random
import stripe
import base64
import json
import io

# Pages initialization
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
        }



@routes.route('/signup', methods=['POST'])
def signup_post():

    # Determining if the user has clicked the email link or not
    if request.json.get('token'):
        try: 
            user_info = decode_token(request.json.get('token'))
            stage = 'SignUpAfter'
        except: return {'error': 'Error decoding token'}
    else:
        stage = 'SignUpBefore'
        email = request.json.get('email').lower()


    # The user has not requested an email yet
    if stage == 'SignUpBefore':

        user = get_user_data(request.json.get('email').lower())
        if user: return {'error': 'User with this email already exists'}

        email_payload = {
            'email': email,
            'action': 'signUp',
            'expiry': (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }

        token = encode_token(email_payload)
        send_email_from_template(email = email, template = 'signUp', payload = token)
        return {'message': 'Confirmation email sent'}


    # The user came after clicking the email link
    if stage == 'SignUpAfter':

        password_encrypted = generate_password_hash(request.json.get('password'))

        execute_query("UPDATE users SET name = %s, auth_type = 'password', password = %s WHERE email = %s", (request.json.get('name'), password_encrypted, user_info['email']))

        user_info['name'] = request.json.get('name')
        user_info['subscription'] = 'none'
        del user_info['onboarding']

        token = encode_token(user_info)
        return {'token': token}



@routes.route('/signup', methods=['GET'])
def signup_get():

    try: email_payload = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return {'error': 'linkExpired'}
    if get_user_data(email_payload['email']): return {'critical': 'User has already been set up'}

    execute_query("INSERT INTO users (email) VALUES (%s)", (email_payload['email'],))

    user_info = email_payload
    user_info['onboarding'] = True

    token = encode_token(user_info)
    return {'token': token, 'action': 'signUpAfter'}



@routes.route('/login', methods=['POST'])
def login_post():

    try: user = get_user_data(request.json.get('email').lower())
    except: return {'error': 'Error retrieving user data'}

    if not user: return {'error': 'User not found'}
    if user['auth_type'] != 'password': return {'error': 'Account exists, but the authentication method is incorrect. Try other methods.'}
    if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'Invalid credentials'}

    user_info = {
        'email': user['email'],
        'name': user['name'],
        'auth_type': user['auth_type'],
        'subscription': user['subscription'],
        'stripe_subscription_id': user['stripe_subscription_id'],
        'stripe_user_id': user['stripe_user_id'],
    }

    token = encode_token(user_info)
    return {'token': token}


@routes.route('/reset-password', methods=['POST'])
def reset_password_post():

    if request.json.get('action') == 'resetPasswordBefore':

        user = get_user_data(request.json.get('email').lower())
        if not user: return {'error': 'User does not exist'}

        email_payload = {
            'email': request.json.get('email').lower(),
            'action': 'resetPasswordAfter',
            'expiry': (datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }

        token = encode_token(email_payload)
        send_email_from_template(email = request.json.get('email').lower(), template = 'resetPassword', payload = token)
        execute_query("UPDATE users SET link_token = %s WHERE email = %s", (token, request.json.get('email').lower()))
        return {'message': 'Confirmation email sent'}
    
    elif request.json.get('action') == 'resetPasswordAfter':

        try: user_info = decode_token(request.json.get('token'))
        except: return {'error': 'Error decoding token'}

        password_encrypted = generate_password_hash(request.json.get('password'))
        execute_query("UPDATE users SET password = %s WHERE email = %s", (password_encrypted, user_info['email']))

        return {'message': 'Password reset successful'}
    

@routes.route('/reset-password', methods=['GET'])
def reset_password_get():

    try: email_payload = decode_token(request.args.get('token'))
    except: return {'error': 'Error decoding token'}

    # Compare current time with expiry time
    if not check_timestamp(email_payload['expiry']): return {'error': 'linkExpired'}

    user = get_user_data(email_payload['email'].lower())
    if not user: return {'error': 'User does not exist'}
    if user['link_token'] != request.args.get('token'): return {'error': 'linkExpired'}

    execute_query("UPDATE users SET link_token = %s WHERE email = %s", (None, email_payload['email'].lower()))

    return {}


@routes.route('/authenticate', methods=['POST'])
def authenticate_post():

    user = get_user_data(request.json.get('email').lower())
    if not user:
        execute_query("INSERT INTO users (email, name, auth_type, supabase_user_id) VALUES (%s, %s, %s, %s)", (
            request.json.get('email').lower(), request.json.get('name'), 
            request.json.get('auth_type'), request.json.get('id')
            ))
        
    token = encode_token({'email': request.json.get('email').lower()})
    return {'token': token}


@routes.route('/subscribe', methods=['POST'])
def subscribe_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    if request.json.get('operation') == 'subscribe':

        user = get_user_data(user_info['email'])

        if not user['stripe_user_id']:
            response = stripe.Customer.create(name = user['name'], email = user['email'])
            execute_query("UPDATE users SET stripe_user_id = %s WHERE email = %s", (response['id'], user_info['email']))
            customer = response['id']

        else: customer = user['stripe_user_id']

        session = stripe.checkout.Session.create(
            customer=customer,
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price': current_app.config[f'STRIPE_PRODUCT_{request.json.get("subscriptionType").upper()}_{request.json.get("periodType").upper()}'], 
                'quantity': 1
                }],
            mode='subscription',
            allow_promotion_codes = True,
            success_url = f"{current_app.config['REDIRECT_URL']}/dashboard",
            cancel_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
        )

        return {'sessionId': session['id']}

    elif request.json.get('operation') == 'manageSubscription':

        session = stripe.billing_portal.Session.create(customer = user_info['stripe_user_id'], return_url = f"{current_app.config['REDIRECT_URL']}/dashboard",)
        return {'sessionUrl': session['url']}
    

@routes.route('/webhook', methods=['POST'])
def webhook_post():

    event = stripe.Webhook.construct_event(request.data, request.headers.get('stripe-signature'), current_app.config['STRIPE_WEBHOOK_KEY_TEST'])
    response = event['data']['object']

    try:
        if event['type'] == 'customer.subscription.created' or event['type'] == 'customer.subscription.updated':
            if response['plan']['id'] == current_app.config['STRIPE_PRODUCT_BASIC_MONTHLY'] or response['plan']['id'] == current_app.config['STRIPE_PRODUCT_BASIC_YEARLY']: product = 'basic'
            elif response['plan']['id'] == current_app.config['STRIPE_PRODUCT_PREMIUM_MONTHLY'] or response['plan']['id'] == current_app.config['STRIPE_PRODUCT_PREMIUM_YEARLY']: product = 'premium'
            execute_query("UPDATE users SET subscription = %s, stripe_subscription_id = %s WHERE stripe_user_id = %s", (product, response['id'], response['customer']))

        elif response['type'] == 'customer.subscription.deleted':
            execute_query("UPDATE users SET subscription = 'none', stripe_subscription_id = NULL WHERE stripe_user_id = %s", (response['customer'],))

    except KeyError: pass

    return {}


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
    
    elif request.json.get('action') == 'deleteAccount': # NOT FINISHED YET

        if user['auth_type'] == 'password':
            if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'Password is not correct'}
        
        if user['auth_type'] != 'password': 
            if user_info['captcha_answer'] != request.json.get('captcha'): return {'error': 'Captcha is not correct'}

        if user['stripe_user_id']: stripe.Customer.delete(user['stripe_user_id'])
        # if user['supabase_user_id']: supabase.auth.delete_user(user['supabase_user_id']) Shit does not work because supabase has no support for python

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
