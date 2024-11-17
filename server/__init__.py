import asyncio
from langchain_openai import ChatOpenAI
from logging.handlers import TimedRotatingFileHandler
from psycopg2.extras import RealDictCursor
from flask_socketio import SocketIO
from flask_cors import CORS
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from flask import Flask, send_from_directory, render_template

import psycopg2
import logging
import stripe
import os

load_dotenv('.env', override=True)
flask_key_secret = os.getenv('flask_key_secret')

socketio = SocketIO(cors_allowed_origins="*", message_queue='redis://')
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key='sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS')

log_filename = os.path.join("database/logs", f"{datetime.now().strftime('%d-%m-%Y')}.log")
handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=90)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

def create_app(mode):

    from .general.routes import routes as general_routes
    from .authentication.routes import routes as auth_routes
    from .dashboard.routes import routes as dashboard_routes
    from .subscription.routes import routes as subscription_routes
    from .github.routes import routes as github_routes

    app = Flask(__name__, static_folder='../client/dist', template_folder='../client/dist')

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # No event loop, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Allowing CORS
    CORS(app)

    if mode == 'prod':
        app.config['MODE'] = 'prod'
        app.config['REDIRECT_URL'] = os.getenv('REDIRECT_URL')
        # app.config['REDIRECT_URL'] = 'http://localhost:5000'

         # Using client built static files in prod version
        @app.route('/')
        @app.route('/<path:path>')
        def serve_index(path=''):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return render_template('index.html')

    elif mode == 'dev':
        app.config['MODE'] = 'dev'
        app.config['REDIRECT_URL'] = 'http://localhost:8080'

    # Initializing environment variables
    app.config['FLASK_KEY_SECRET'] = os.getenv('FLASK_KEY_SECRET')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['MAIL_SENDER_USER'] = os.getenv('MAIL_SENDER_USER')
    app.config['MAIL_SENDER_PASS'] = os.getenv('MAIL_SENDER_PASS')
    app.config['MAIL_CONTACT_USER'] = os.getenv('MAIL_CONTACT_USER')

    app.config['STRIPE_WEBHOOK_KEY'] = os.getenv('STRIPE_WEBHOOK_KEY')
    app.config['STRIPE_PRODUCT_BASIC_MONTHLY'] = os.getenv('STRIPE_PRODUCT_BASIC_MONTHLY')
    app.config['STRIPE_PRODUCT_BASIC_YEARLY'] = os.getenv('STRIPE_PRODUCT_BASIC_YEARLY')
    app.config['STRIPE_PRODUCT_PREMIUM_MONTHLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_MONTHLY')
    app.config['STRIPE_PRODUCT_PREMIUM_YEARLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_YEARLY')
    app.config['STRIPE_PRODUCT_REPLENISH'] = os.getenv('STRIPE_PRODUCT_REPLENISH')

    app.config['TELEGRAM_BOT_KEY'] = os.getenv('TELEGRAM_BOT_KEY')

    app.config['INIT_LOGS_SENT'] = False

    stripe.api_key = os.environ.get('STRIPE_KEY')
    supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

    # Registering routes
    app.register_blueprint(general_routes, name='general', url_prefix='/api/')
    app.register_blueprint(auth_routes, name='auth', url_prefix='/api/')
    app.register_blueprint(subscription_routes, name='subscription', url_prefix='/api/')
    app.register_blueprint(dashboard_routes, name='dashboard', url_prefix='/api/')
    app.register_blueprint(github_routes, name='github', url_prefix='/gh/')
    socketio.init_app(app)

    return app, socketio
