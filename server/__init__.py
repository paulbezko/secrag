from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi_socketio import SocketManager
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from server.globals import config as dashboard_config
from logtail import LogtailHandler

import logging
import stripe
import os

load_dotenv('.env', override=True)
flask_key_secret = os.getenv('flask_key_secret')

log_filename = os.path.join("database/logs", f"{datetime.now().strftime('%d-%m-%Y')}.log")
handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=90)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

config = {}

def create_app(mode: str):

    app = FastAPI()
    socketio = SocketManager(app, cors_allowed_origins="*", mount_location="/socket.io")



    #######################################################################
    ###                         LOAD ROUTES                             ###
    from server.general.routes import routes as general_routes
    from server.authentication.routes import routes as auth_routes
    from server.dashboard.routes import routes as dashboard_routes
    from server.subscription.routes import routes as subscription_routes
    from server.github.routes import routes as github_routes

    from server.v2.routes import routes as v2_routes

    # app.include_router(general_routes, prefix="/api")
    # app.include_router(auth_routes, prefix="/api")
    # app.include_router(subscription_routes, prefix="/api")
    # app.include_router(dashboard_routes, prefix="/api")
    # app.include_router(github_routes, prefix="/gh")

    app.include_router(v2_routes, prefix="/api")

    #######################################################################
    ###                         SERVE INDEX                             ### 
    if mode == 'prod':

        #######################################################################
        ###                         LOAD CLIENT                             ###
        app.mount("/css", StaticFiles(directory="client/dist/css"), name="css")
        app.mount("/js", StaticFiles(directory="client/dist/js"), name="js")
        app.mount("/img", StaticFiles(directory="client/dist/img"), name="img")

        templates = Jinja2Templates(directory="client/dist")

        css_file_path = Path(__file__).parent.parent / "client" / "dist" / "style.css"
        robots_file_path = Path(__file__).parent.parent / "client" / "dist" / "robots.txt"
        sitemap_file_path = Path(__file__).parent.parent / "client" / "dist" / "sitemap.xml"
        
        @app.get("/style.css")
        async def serve_css():
            return FileResponse(css_file_path)
        @app.get("/robots.txt")
        async def serve_robots():
            return FileResponse(robots_file_path)
        @app.get("/sitemap.xml")
        async def serve_sitemap():
            return FileResponse(sitemap_file_path)
        
        app.mount("/style", StaticFiles(directory="client/dist/style"), name="style")

        config['MODE'] = 'prod'
        config['REDIRECT_URL'] = os.getenv('REDIRECT_URL', 'http://localhost:5000')
        # Serve index page
        @app.get("/{full_path:path}", response_class=HTMLResponse)
        async def serve_index(request: Request):
            return templates.TemplateResponse("index.html", {"request": request})

    elif mode == 'dev':
        config['MODE'] = 'dev'
        config['REDIRECT_URL'] = 'http://localhost:8080'
    
    #######################################################################
    ###                 LOAD ENVIRONMENTAL VARIABLES                    ###
    config['FLASK_KEY_SECRET'] = os.getenv('FLASK_KEY_SECRET')
    config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    config['MAIL_SENDER_USER'] = os.getenv('MAIL_SENDER_USER')
    config['MAIL_SENDER_PASS'] = os.getenv('MAIL_SENDER_PASS')
    config['MAIL_CONTACT_USER'] = os.getenv('MAIL_CONTACT_USER')

    # Stripe keys
    config['STRIPE_WEBHOOK_KEY'] = os.getenv('STRIPE_WEBHOOK_KEY')
    config['STRIPE_PRODUCT_BASIC_MONTHLY'] = os.getenv('STRIPE_PRODUCT_BASIC_MONTHLY')
    config['STRIPE_PRODUCT_BASIC_YEARLY'] = os.getenv('STRIPE_PRODUCT_BASIC_YEARLY')
    config['STRIPE_PRODUCT_PREMIUM_MONTHLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_MONTHLY')
    config['STRIPE_PRODUCT_PREMIUM_YEARLY'] = os.getenv('STRIPE_PRODUCT_PREMIUM_YEARLY')
    config['STRIPE_PRODUCT_REPLENISH'] = os.getenv('STRIPE_PRODUCT_REPLENISH')

    config['TELEGRAM_BOT_KEY'] = os.getenv('TELEGRAM_BOT_KEY')

    config['INIT_LOGS_SENT'] = False

    dashboard_config.set(config)

    #######################################################################
    ###                         MISCELLANEOUS                           ###
    stripe.api_key = os.environ.get('STRIPE_KEY')
    supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"], 
    )
    
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(LogtailHandler(source_token='r7bKwtvkMf9iBBqAsYXmJyFS'))

    # Return the FastAPI app and SocketIO instance for use
    return app, socketio

