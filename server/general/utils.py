from email.mime.multipart import MIMEMultipart
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
    chat_id = '-4506773539'
    for i in range(0, len(message), 4000):
        chunk = message[i:i + 4000]
        requests.post(f"https://api.telegram.org/bot{current_app.config['TELEGRAM_BOT_KEY']}/sendMessage", data={'chat_id': chat_id, 'text': chunk})


def encode_token(payload):
    try: return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm="HS256")
    except Exception as error: return error


def decode_token(token):
    try: return jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
    except Exception as error: return error


def send_email_from_template(email, template, payload):

    head = f"""
        <head>
            <style>
                .container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 20px;
                    max-width: 600px;
                    margin: auto;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                }}
                .button {{
                    background-color: #FFC107;
                    color: #2D2D2D;
                    max-width: fit-content;
                    cursor: pointer;
                    font-family: 'Inter', sans-serif;
                    font-weight: 700;
                    font-size: var(--text-button);
                    border-radius: 40rem;
                    padding-inline: 4rem;
                    padding-block: 1rem;
                    transition: all 0.3s ease;
                }}

                .button:hover {{
                    background-color: #FFD350
                }}
            </style>
        </head>
    """
    
    # Define HTML templates for each email type
    templates = {
        'signUp': {
            'subject': 'Welcome to SkelTal!',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <h2>Welcome to SkelTal!</h2>
                            <p>Click the button below to verify your email address:</p>
                            <a class="button" href="{current_app.config['REDIRECT_URL']}/signup?token={payload}">Verify Email</a>
                            <p>If you did not sign up for this account, please ignore this email.</p>
                        </div>
                    </body>
                </html>
            """
        },
        'resetPassword': {
            'subject': 'Reset Password',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <h2>Reset Your Password</h2>
                            <p>Click the button below to reset your password:</p>
                            <a class="button" href="{current_app.config['REDIRECT_URL']}/reset-password?token={payload}">Reset Password</a>
                            <p>If you did not request a password reset, please ignore this email.</p>
                        </div>
                    </body>
                </html>
            """
        },
        'changeEmail': {
            'subject': 'Change Email Confirmation',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <h2>Confirm Your Email Change</h2>
                            <p>Click the button below to confirm your new email address:</p>
                            <a class="button" href="{current_app.config['REDIRECT_URL']}/change-email?token={payload}">Confirm Email</a>
                            <p>If you did not request an email change, please ignore this email.</p>
                        </div>
                    </body>
                </html>
            """
        }
    }
    
    # Check if the template exists
    if template not in templates:
        return log('error', f'Error [Send Email]: Invalid email type "{template}"')

    # Extract subject and body
    subject = templates[template]['subject']
    html_body = templates[template]['html_body']

    try:
        # Create a multipart email
        email_message = MIMEMultipart('alternative')
        email_message['Subject'] = subject
        email_message['From'] = current_app.config['MAIL_SENDER_USER']
        email_message['To'] = email
        
        # Attach the HTML version
        email_message.attach(MIMEText(html_body, 'html'))

        # Send the email
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
                query = f"SELECT * FROM users_{current_app.config['MODE']} WHERE email = %s"
                cursor.execute(query, (email,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            reconnect_to_db()
            time.sleep(1)
        
        except Exception as error:
            log('error', f'Error [Get User Data]: {error}')
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


def try_except(func, default=None, expected_exc=(Exception,)):
    """
    Tries to execute a given function, and if it fails with one of the specified
    exceptions, returns a default value instead.

    :param func: The function to try to execute
    :param default: The value to return if an exception is raised
    :param expected_exc: A tuple of exception types that are expected to be raised
    :return: The result of the function, or the default value if an exception was
             raised
    """
    try: return func()
    except expected_exc: return default
