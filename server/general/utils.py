from email.mime.text import MIMEText
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from psycopg2 import OperationalError, InterfaceError
from flask import current_app

import psycopg2
import requests
import smtplib
import time
import jwt
import os


def log(level, message):
    if level == 'debug': 
        current_app.logger.debug(message)
        # log_telebot("DEBUG\n\n" + message)
    elif level == 'info': 
        current_app.logger.info(message)
        # log_telebot("INFO\n\n" + message)
    elif level == 'warning': 
        current_app.logger.warning(message)
        # log_telebot("WARNING\n\n" + message)
    elif level == 'error': 
        current_app.logger.error(message)
        log_telebot("ERROR\n\n" + message)
    else: 
        current_app.logger.critical(message)
        log_telebot("CRITICAL\n\n" + message)


def log_telebot(message):
    requests.post(f"https://api.telegram.org/bot{current_app.config['TELEGRAM_BOT_KEY']}/sendMessage", data={'chat_id': '-4506773539', 'text': message})


def encode_token(payload):
    try: return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm="HS256")
    except Exception as error: return error


def decode_token(token):
    try: return jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
    except Exception as error: return error


def send_email_from_template(email, template, payload):
    
    if template == 'signUp':
        subject = 'Welcome to SkelTal!'
        body = f"Click the link below to verify your email address: {current_app.config['REDIRECT_URL']}/signup?token={payload}"

    elif template == 'resetPassword':
        subject = 'Reset Password'
        body = f"Click the link below to reset your password: {current_app.config['REDIRECT_URL']}/reset-password?token={payload}"

    elif template == 'changeEmail':
        subject = 'Change Email'
        body = f"Click the link below to confirm your email: {current_app.config['REDIRECT_URL']}/change-email?token={payload}"

    elif template == 'contact':
        subject = 'New contact request submitted.'
        body = payload

    else: return print('Error [Send Email]: Invalid email type')

    try:
        email_message = MIMEText(body)
        email_message['Subject'] = subject
        email_message['From'] = current_app.config['MAIL_SENDER_USER']
        email_message['To'] = email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(current_app.config['MAIL_SENDER_USER'], current_app.config['MAIL_SENDER_PASS'])
            smtp_server.send_message(email_message)
        log('debug', f'Email of type "{template}" sent successfully to {email}')

    except Exception as error:
        log('error', f'Error [Send Email]: {error}')


def get_user_data(email, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            log('error', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            reconnect_to_db()
            time.sleep(1)
        
        except Exception as error:
            log('warning', f'Error [Get User Data]: {error}')
            break
    
    log('critical', 'Failed to retrieve user data after multiple attempts.')
    return None


def execute_query(query, params, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
            return  # Exit function after successful execution
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            reconnect_to_db()
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            log('error', f'Error [Execute Query]: {error}')
            break  # Exit loop on unexpected exceptions

    log('critical', 'Failed to execute query after multiple attempts.')


def reconnect_to_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            cursor_factory=RealDictCursor
        )
        current_app.config['DB_CONNECTION'] = connection
        log('debug', 'Reconnected to database successfully.')
    except OperationalError as error:
        log('error', f'Error [Reconnect to Database]: {error}')


def check_timestamp(timestamp):

    if datetime.now(timezone.utc) > datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc): return False
    else: return True