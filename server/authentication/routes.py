from werkzeug.security import check_password_hash, generate_password_hash
from ..general.utils import get_user_data, encode_token, decode_token, send_email_from_template, execute_query, check_timestamp, log
from datetime import datetime, timezone, timedelta
from flask import request, Blueprint, current_app

# Routes initialization
routes = Blueprint('routes', __name__)


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
        log('debug', f'Signup email sent to {email}')
        return {'message': 'Confirmation email sent'}


    # The user came after clicking the email link
    if stage == 'SignUpAfter':

        password_encrypted = generate_password_hash(request.json.get('password'))

        log('debug', f'User account created for {user_info['email']}')
        log('info', f'New user joined through email: {user_info['email']}')
        query = f"UPDATE users_{current_app.config['MODE']} SET name = %s, auth_type = 'password', password = %s WHERE email = %s"
        execute_query(query, (request.json.get('name'), password_encrypted, user_info['email']))

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
    if get_user_data(email_payload['email']): return {'critical': 'userExists'}

    log('debug', f'Signup email confirmed for {email_payload['email']}')
    query = f"INSERT INTO users_{current_app.config['MODE']} (email) VALUES (%s)"
    execute_query(query, (email_payload['email'],))

    user_info = email_payload
    user_info['onboarding'] = True

    token = encode_token(user_info)
    return {'token': token}


@routes.route('/login', methods=['POST'])
def login_post():

    try: user = get_user_data(request.json.get('email').lower())
    except: return {'error': 'Error retrieving user data'}

    if not user: return {'error': 'userNotFound'}
    if user['auth_type'] != 'password': return {'error': 'authMethodIncorrect'}
    if not check_password_hash(user['password'], request.json.get('password')): return {'error': 'invalidCredentials'}

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
        query = f"UPDATE users_{current_app.config['MODE']} SET link_token = %s WHERE email = %s"
        execute_query(query, (token, request.json.get('email').lower()))
        return {'message': 'Confirmation email sent'}
    
    elif request.json.get('action') == 'resetPasswordAfter':

        try: user_info = decode_token(request.json.get('token'))
        except: return {'error': 'Error decoding token'}

        password_encrypted = generate_password_hash(request.json.get('password'))
        query = f"UPDATE users_{current_app.config['MODE']} SET password = %s, WHERE email = %s"
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

    query = f"UPDATE users_{current_app.config['MODE']} SET link_token = %s WHERE email = %s"
    execute_query(query, (None, email_payload['email'].lower()))

    return {}


@routes.route('/authenticate', methods=['POST'])
def authenticate_post():

    user = get_user_data(request.json.get('email').lower())
    if not user:
        log('info', f'New user joined through Google: {request.json.get('email').lower()}')
        query = f"INSERT INTO users_{current_app.config['MODE']} (email, name, auth_type, supabase_user_id) VALUES (%s, %s, %s, %s)"
        execute_query(query, (request.json.get('email').lower(), request.json.get('name'), request.json.get('auth_type'), request.json.get('id')))
        user_info = {
            'email': request.json.get('email').lower(),
            'name': request.json.get('name'),
            'auth_type': 'google',
        }

    elif user['auth_type'] == 'google': 
        user_info = {
            'email': request.json.get('email').lower(),
            'name': user['name'],
            'auth_type': user['auth_type'],
            'subscription': user['subscription'],
            'subscription_tokens_left': user['subscription_tokens_left'],
            'stripe_subscription_id': user['stripe_subscription_id'],
            'stripe_user_id': user['stripe_user_id'],
        }
    else: return {'error': 'authMethodIncorrect'}

    token = encode_token(user_info)
    return {'token': token}