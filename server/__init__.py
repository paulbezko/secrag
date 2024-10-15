from langchain_openai import ChatOpenAI
from psycopg2.extras import RealDictCursor
from flask_socketio import SocketIO
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
from flask import Flask, send_from_directory, render_template

import psycopg2
import stripe
import os

load_dotenv('.env', override=True)
flask_key_secret = os.getenv('flask_key_secret')

from flask_socketio import SocketIO, emit
socketio = SocketIO(cors_allowed_origins="*", message_queue='redis://')
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key='sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS')

def create_app(mode):

    from .routes import routes
    app = Flask(__name__, static_folder='../client/dist', template_folder='../client/dist')

    # Allowing CORS
    CORS(app)

    if mode == 'prod':
        app.config['REDIRECT_URL'] = os.getenv('REDIRECT_URL')

         # Using client built static files in prod version
        @app.route('/')
        @app.route('/<path:path>')
        def serve_index(path=''):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return render_template('index.html')

    elif mode == 'dev':
        app.config['REDIRECT_URL'] = 'http://localhost:8080'
        
    # Initializing database
    connection = psycopg2.connect(
        host        = os.getenv('DB_HOST'),
        port        = os.getenv('DB_PORT'),
        database    = os.getenv('DB_NAME'),
        user        = os.getenv('DB_USER'),
        password    = os.getenv('DB_PASS'),
        cursor_factory = RealDictCursor
    )
    app.config['DB_CONNECTION'] = connection

    # Initializing environment variables
    app.config['FLASK_KEY_SECRET'] = os.getenv('FLASK_KEY_SECRET')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['MAIL_SENDER_USER'] = os.getenv('MAIL_SENDER_USER')
    app.config['MAIL_SENDER_PASS'] = os.getenv('MAIL_SENDER_PASS')
    app.config['MAIL_CONTACT_USER'] = os.getenv('MAIL_CONTACT_USER')

    app.config['STRIPE_WEBHOOK_KEY_TEST'] = os.getenv('STRIPE_WEBHOOK_KEY_TEST')
    app.config['STRIPE_PRODUCT_BASIC_MONTHLY'] = os.getenv('STRIPE_PRODUCT_BASIC_MONTHLY')
    app.config['STRIPE_PRODUCT_BASIC_YEARLY'] = os.getenv('STRIPE_PRODUCT_BASIC_YEARLY')
    app.config['STRIPE_PRODUCT_PREMIUM_MONTHLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_MONTHLY')
    app.config['STRIPE_PRODUCT_PREMIUM_YEARLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_YEARLY')
    app.config['STRIPE_PRODUCT_REPLENISH'] = os.getenv('STRIPE_PRODUCT_REPLENISH')

    stripe.api_key = os.environ.get('STRIPE_KEY_TEST')
    supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

    # Registering routes
    app.register_blueprint(routes, url_prefix='/api/')
    socketio.init_app(app)

    return app
