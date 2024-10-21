from ..general.utils import get_user_data, decode_token, execute_query, log
from .utils import get_user_data_stripe
from flask import request, Blueprint, current_app

import stripe

# Routes initialization
routes = Blueprint('routes', __name__)

@routes.route('/subscribe', methods=['POST'])
def subscribe_post():

    try: user_info = decode_token(request.json.get('token'))
    except: return {'error': 'Error decoding token'}

    if request.json.get('operation') == 'subscribe':

        user = get_user_data(user_info['email'])

        if not user['stripe_user_id']:
            response = stripe.Customer.create(name = user['name'], email = user['email'])
            log('debug', f'Stripe user created: {response}')
            query = f"UPDATE users_{current_app.config['MODE']} SET stripe_user_id = %s WHERE email = %s"
            execute_query(query, (response['id'], user_info['email']))
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

    elif request.json.get('operation') == 'replenishTokens':

        user = get_user_data(user_info['email'])
        customer = user['stripe_user_id']

        session = stripe.checkout.Session.create(
            customer=customer,
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price': current_app.config[f'STRIPE_PRODUCT_REPLENISH'], 
                'quantity': 1
                }],
            mode='payment',
            allow_promotion_codes = True,
            success_url = f"{current_app.config['REDIRECT_URL']}/dashboard",
            cancel_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
        )
        return {'sessionUrl': session['url']}
    

@routes.route('/webhook', methods=['POST'])
def webhook_post():

    event = stripe.Webhook.construct_event(request.data, request.headers.get('stripe-signature'), current_app.config['STRIPE_WEBHOOK_KEY'])
    response = event['data']['object']

    try:
        if 'type' in event:
            if event['type'] == 'checkout.session.completed': 

                user = get_user_data_stripe(response['customer'])
                log('debug', f'User completed checkout session: {user["email"]}')
                query = f"UPDATE users_{current_app.config['MODE']} SET subscription_tokens_left = %s WHERE stripe_user_id = %s"
                execute_query(query, (int(user['subscription_tokens_left']) + 1200, response['customer']))

            elif event['type'] == 'customer.subscription.created' or event['type'] == 'customer.subscription.updated':

                try: user = get_user_data_stripe(response['customer'])
                except: return {'error': 'Error retrieving user data'}
                

                if response['plan']['id'] == current_app.config['STRIPE_PRODUCT_BASIC_MONTHLY'] or response['plan']['id'] == current_app.config['STRIPE_PRODUCT_BASIC_YEARLY']: 
                    tokens = 1200
                    product = 'basic'
                elif response['plan']['id'] == current_app.config['STRIPE_PRODUCT_PREMIUM_MONTHLY'] or response['plan']['id'] == current_app.config['STRIPE_PRODUCT_PREMIUM_YEARLY']: 
                    tokens = 2400
                    product = 'premium'
                    
                if user['subscription_tokens_left'] != None:
                    tokens += int(user['subscription_tokens_left'])

                log('debug', f'User completed checkout session: {user["email"]}')
                query = f"UPDATE users_{current_app.config['MODE']} SET subscription = %s, subscription_tokens_left = %s, stripe_subscription_id = %s WHERE stripe_user_id = %s"
                execute_query(query, (product, tokens, response['id'], response['customer']))

            elif event['type'] == 'customer.subscription.deleted':

                log('debug', f'User canceled subscription: {response["customer"]}')
                query = f"UPDATE users_{current_app.config['MODE']} SET subscription = 'none', subscription_tokens_left = 0, stripe_subscription_id = NULL WHERE stripe_user_id = %s"
                execute_query(query, (response['customer'],))

    except Exception as error: log('error', f'Error in webhook: {error}')
    return {}