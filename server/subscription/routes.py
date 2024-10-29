from ..general.utils import get_user_data, decode_token, execute_query, log, send_email_from_template
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
            success_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
            cancel_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
        )
        return {'sessionId': session['id']}

    elif request.json.get('operation') == 'manageSubscription':

        session = stripe.billing_portal.Session.create(
            customer = user_info['stripe_user_id'], 
            return_url = f"{current_app.config['REDIRECT_URL']}/dashboard?after-billing=true",
        )
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
            success_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
            cancel_url = f"{current_app.config['REDIRECT_URL']}/subscribe",
            metadata = {"replenishTokens": "True"}
        )
        return {'sessionUrl': session['url']}
    

@routes.route('/webhook', methods=['POST'])
def webhook_post():

    event = stripe.Webhook.construct_event(request.data, request.headers.get('stripe-signature'), current_app.config['STRIPE_WEBHOOK_KEY'])
    response = event['data']['object']
    try:
        if 'type' in event:

            if event['type'] == 'invoice.payment_succeeded': # User paid invoice for subscription
                user = get_user_data_stripe(response['customer'])
                log('debug', f'User paid invoice: {user["email"]}')

                price_id = response['lines']['data'][-1]['price']['id']
                amount = response['amount_paid']

                if int(amount) == 0: # Handle 100% coupon
                    amount = response['lines']['data'][-1]['plan']['amount']

                if price_id == current_app.config['STRIPE_PRODUCT_PREMIUM_YEARLY']: subscription = 'premium'
                elif price_id == current_app.config['STRIPE_PRODUCT_PREMIUM_MONTHLY']: subscription = 'premium'
                elif price_id == current_app.config['STRIPE_PRODUCT_BASIC_YEARLY']: subscription = 'basic'
                elif price_id == current_app.config['STRIPE_PRODUCT_BASIC_MONTHLY']: subscription = 'basic'

                tokens = 0
                if amount > 0: tokens += round(amount * 1.2) # Add tokens if user spent money
                if int(user['subscription_tokens_left']) != 0: tokens += int(user['subscription_tokens_left'])

                query = f"UPDATE users_{current_app.config['MODE']} SET subscription = %s, subscription_tokens_left = %s WHERE stripe_user_id = %s"
                execute_query(query, (subscription, tokens, response['customer']))
                send_email_from_template(user['email'], 'subscribe', None)

            elif event['type'] == 'customer.subscription.deleted': # User cancelled subscription
                user = get_user_data_stripe(response['customer'])
                log('debug', f'User cancelled subscription: {user["email"]}')

                query = f"UPDATE users_{current_app.config['MODE']} SET subscription = 'none', stripe_subscription_id = NULL WHERE stripe_user_id = %s" # Do not clear tokens when subscription cancels
                execute_query(query, (response['customer'],))
                send_email_from_template(user['email'], 'unsubscribe', None)

            elif event['type'] == 'checkout.session.completed': # User paid invoice for token renewal
                if 'replenishTokens' in response['metadata']:

                    user = get_user_data_stripe(response['customer'])
                    log('debug', f'User bought tokens: {user["email"]}')

                    tokens = 1200
                    if user['subscription_tokens_left'] != 0: tokens += int(user['subscription_tokens_left'])

                    query = f"UPDATE users_{current_app.config['MODE']} SET subscription_tokens_left = %s WHERE stripe_user_id = %s"
                    execute_query(query, (tokens, response['customer']))
                    send_email_from_template(user['email'], 'purchase', None)


    except Exception as error: log('error', f'Error in webhook: {error}')
    return {}