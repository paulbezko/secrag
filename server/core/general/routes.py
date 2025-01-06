from fastapi.responses import JSONResponse
from jinja2 import Template
from .utils import get_user_data, encode_token, decode_token, log

from fastapi import APIRouter

routes = APIRouter()

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