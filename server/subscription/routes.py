from fastapi.responses import JSONResponse
from ..general.utils import get_user_data, decode_token, execute_query, log, send_email_from_template
from .utils import get_user_data_stripe
from ..globals import config

import stripe

from fastapi import APIRouter, Request

routes = APIRouter()

@routes.post('/subscribe')
async def subscribe_post(request: Request):
    data = await request.json()
    token = data.get("token")
    operation = data.get("operation")

    try: user_info = decode_token(token)
    except: return JSONResponse(content={'error': 'Error decoding token'})

    if operation == 'subscribe':

        user = get_user_data(user_info['email'])

        if not user['stripe_user_id']:
            response = stripe.Customer.create(name = user['name'], email = user['email'])
            log('debug', f'Stripe user created: {user['email']}')
            query = f"UPDATE users_{config.get('MODE')} SET stripe_user_id = %s WHERE email = %s"
            execute_query(query, (response['id'], user_info['email']))
            customer = response['id']

        else: customer = user['stripe_user_id']

        session = stripe.checkout.Session.create(
            customer=customer,
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price': config[f'STRIPE_PRODUCT_{request.json.get("subscriptionType").upper()}_{request.json.get("periodType").upper()}'], 
                'quantity': 1
                }],
            mode='subscription',
            allow_promotion_codes = True,
            success_url = f"{config.get('REDIRECT_URL')}/dashboard",
            cancel_url = f"{config.get('REDIRECT_URL')}/subscribe",
        )
        return JSONResponse(content={'sessionId': session['id']})

    elif operation == 'manageSubscription':

        session = stripe.billing_portal.Session.create(
            customer = user_info['stripe_user_id'], 
            return_url = f"{config.get('REDIRECT_URL')}/dashboard?after-billing=true",
        )
        return JSONResponse(content={'sessionUrl': session['url']})

    elif operation == 'replenishTokens':

        user = get_user_data(user_info['email'])
        customer = user['stripe_user_id']

        session = stripe.checkout.Session.create(
            customer=customer,
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price': config.get(f'STRIPE_PRODUCT_REPLENISH'), 
                'quantity': 1
                }],
            mode='payment',
            allow_promotion_codes = True,
            success_url = f"{config.get('REDIRECT_URL')}/dashboard?after-billing=true",
            cancel_url = f"{config.get('REDIRECT_URL')}/dashboard",
            metadata = {"replenishTokens": "True"}
        )
        return JSONResponse(content={'sessionUrl': session['url']})
    

@routes.post('/webhook')
async def webhook_post(request: Request):
    data = await request.body()
    event = stripe.Webhook.construct_event(data, request.headers.get('stripe-signature'), config.get('STRIPE_WEBHOOK_KEY'))
    response = event['data']['object']
    try:
        if 'type' in event:

            if event['type'] == 'invoice.payment_succeeded': # User paid invoice for subscription
                user = get_user_data_stripe(response['customer'])
                log('debug', f'User paid invoice: {user["email"]}')

                price_id = response['lines']['data'][-1]['price']['id']
                amount = response['amount_paid']

                if response['discount']['coupon']['name'] == "ZERO": # Handle ZERO coupon
                    if len(response['lines']['data']) == 1: # Only add tokens if user has one subscription
                        amount = response['lines']['data'][-1]['plan']['amount']
                    else: amount = 0

                if price_id == config.get('STRIPE_PRODUCT_PREMIUM_YEARLY'): subscription = 'premium'
                elif price_id == config.get('STRIPE_PRODUCT_PREMIUM_MONTHLY'): subscription = 'premium'
                elif price_id == config.get('STRIPE_PRODUCT_BASIC_YEARLY'): subscription = 'basic'
                elif price_id == config.get('STRIPE_PRODUCT_BASIC_MONTHLY'): subscription = 'basic'

                tokens = 0
                if amount > 0: tokens += round(amount * 1.2) # Add tokens if user spent money
                user_tokens = int(user['subscription_tokens_left']) if user['subscription_tokens_left'] is not None else 0
                if user_tokens != 0: tokens += int(user['subscription_tokens_left'])

                query = f"UPDATE users_{config.get('MODE')} SET subscription = %s, subscription_tokens_left = %s WHERE stripe_user_id = %s"
                execute_query(query, (subscription, tokens, response['customer']))
                send_email_from_template(user['email'], 'subscribe', None)

            elif event['type'] == 'customer.subscription.deleted': # User cancelled subscription
                user = get_user_data_stripe(response['customer'])
                log('debug', f'User cancelled subscription: {user["email"]}')

                query = f"UPDATE users_{config.get('MODE')} SET subscription = 'none', stripe_subscription_id = NULL WHERE stripe_user_id = %s" # Do not clear tokens when subscription cancels
                execute_query(query, (response['customer'],))
                send_email_from_template(user['email'], 'unsubscribe', None)

            elif event['type'] == 'checkout.session.completed': # User paid invoice for token renewal
                if 'replenishTokens' in response['metadata']:

                    user = get_user_data_stripe(response['customer'])
                    log('debug', f'User bought tokens: {user["email"]}')

                    tokens = 1200
                    if user['subscription_tokens_left'] != 0: tokens += int(user['subscription_tokens_left'])

                    query = f"UPDATE users_{config.get('MODE')} SET subscription_tokens_left = %s WHERE stripe_user_id = %s"
                    execute_query(query, (tokens, response['customer']))
                    send_email_from_template(user['email'], 'purchase', None)


    except Exception as error: log('error', f'Error in webhook: {error}')
    return JSONResponse(content={})