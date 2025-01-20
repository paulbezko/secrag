from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from psycopg2 import OperationalError, InterfaceError
from ...globals import config

import tracemalloc
import logging
import traceback
import psycopg2
import requests
import smtplib
import time
import jwt
import os

tracemalloc.start()

logger = logging.Logger("a")

def log(level, message):
    if level == 'debug': 
        logger.debug(message)
        # log_telebot("DEBUG\n\n" + message)
    elif level == 'info': 
        logger.info(message)
        # log_telebot("INFO\n\n" + message)
    elif level == 'warning': 
        logger.warning(message)
        # log_telebot("WARNING\n\n" + message)
    elif level == 'error': 
        logger.error(message)
        log_telebot("ERROR\n\n" + message)
    else: 
        logger.critical(message)
        log_telebot("CRITICAL\n\n" + message)


def log_telebot(message):
    chat_id = '-4506773539'
    for i in range(0, len(message), 4000):
        chunk = message[i:i + 4000]
        requests.post(f"https://api.telegram.org/bot{config.get('TELEGRAM_BOT_KEY')}/sendMessage", data={'chat_id': chat_id, 'text': chunk})


def encode_token(payload):
    try: return jwt.encode(payload, config.get('JWT_SECRET'), algorithm="HS256")
    except Exception as error: return error


def decode_token(token):
    try: return jwt.decode(token, config.get('JWT_SECRET'), algorithms=["HS256"])
    except Exception as error:
        logger.debug(traceback.format_exc())
        logger.debug(str(error))

        return error


def get_user_data(type, key, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            
            connection = psycopg2.connect(
                host        = os.getenv('DB_HOST'),
                port        = os.getenv('DB_PORT'),
                database    = os.getenv('DB_NAME'),
                user        = os.getenv('DB_USER'),
                password    = os.getenv('DB_PASS'),
                cursor_factory = RealDictCursor
            )
            with connection.cursor() as cursor:
                query = f"SELECT * FROM users_{config.get('MODE')} WHERE {type} = %s"
                cursor.execute(query, (key,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            time.sleep(1)
        
        except Exception as error:
            log('error', f'Error [Get User Data]: {traceback.format_exc()}')
            log('error', f'Error [Get User Data]: {error}')
            break

        finally:
            connection.close()
    
    log('critical', 'Failed to retrieve user data after multiple attempts.')
    return None


def execute_query(query, params, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            connection = psycopg2.connect(
                host        = os.getenv('DB_HOST'),
                port        = os.getenv('DB_PORT'),
                database    = os.getenv('DB_NAME'),
                user        = os.getenv('DB_USER'),
                password    = os.getenv('DB_PASS'),
                cursor_factory = RealDictCursor
            )
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
            return  # Exit function after successful execution
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            log('error', f'Error [Execute Query]: {error}')
            break  # Exit loop on unexpected exceptions

        finally:
            connection.close()

    log('critical', 'Failed to execute query after multiple attempts.')


def send_email_from_template(email, template, payload):

    print(email, template, payload)

    head = f"""
        <head>
            <style>
                .container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 30px;
                    max-width: 400px;
                    margin: auto;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                }}
                .header {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #333;
                    text-align: center;
                }}
                .content {{
                    font-size: 16px;
                    line-height: 1.6;
                    text-align: center;
                    color: #555;
                    margin-top: 20px;
                }}
                .button-container {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .button {{
                    background-color: #FFC107;
                    color: #2D2D2D;
                    padding: 12px 24px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 16px;
                }}
                a:link, span.MsoHyperlink {{
                    mso-style-priority:100 !important;
                    color:#000000 !important;
                    color:#000000;
                    text-decoration:none !important;
                }}
                .signature {{
                    font-size: 14px;
                    color: #333;
                    text-align: center;
                    margin-top: 30px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
    """
    
    # Define HTML templates for each email type
    templates = {
        'signUp': {
            'subject': 'Welcome to SECRAG!',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Welcome to SECRAG!</div>
                            <div class="content">
                                To proceed with setting up your account, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="{config.get('REDIRECT_URL')}?token={payload}">Confirm Email</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not sign up for this account, please disregard this message.</div>
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
                            <div class="header">Reset Your Password</div>
                            <div class="content">
                                To complete your request to reset your password, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="{config.get('REDIRECT_URL')}?token={payload}">Reset Password</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not request this change, please disregard this message.</div>
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
                            <div class="header">Confirm Your Email Address</div>
                            <div class="content">
                                To complete your request to update your email address, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="{config.get('REDIRECT_URL')}/change-email?token={payload}">Confirm Email</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not request this change, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'subscribe': {
            'subject': 'Subscription Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Subscription Was Successful</div>
                            <div class="content">
                                You can now access SECRAG's features in accordance with your subscription.
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not adjust your subscription, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'unsubscribe': {
            'subject': 'Unsubscription Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Unsubscription Was Successful</div>
                            <div class="content">
                                Thank you for using SECRAG!
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not adjust your subscription, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'purchase': {
            'subject': 'Token Purchase Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Token Purchase Was Successful</div>
                            <div class="content">
                                Your token balance has been updated.
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not purchase tokens, please disregard this message.</div>
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
        email_message['From'] = config.get('MAIL_SENDER_USER')
        email_message['To'] = email
        
        # Attach the HTML version
        email_message.attach(MIMEText(html_body, 'html'))

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(config.get('MAIL_SENDER_USER'), config.get('MAIL_SENDER_PASS'))
            smtp_server.send_message(email_message)

        log('debug', f'Email of type "{template}" sent successfully to {email}')

    except Exception as error:
        log('error', f'Error [Send Email]: {error}')


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
    except expected_exc: 
        return default

async def atry_except(func, default=None, expected_exc=(Exception,)):
    """
    Tries to execute a given function, and if it fails with one of the specified
    exceptions, returns a default value instead.

    :param func: The function to try to execute
    :param default: The value to return if an exception is raised
    :param expected_exc: A tuple of exception types that are expected to be raised
    :return: The result of the function, or the default value if an exception was
             raised
    """
    try: return await func()
    except expected_exc: 
        return default


def send_autoupdate_log():
    with open("autoupdate.log", "r") as f:

        autoupdate_log = f.read()
        # with current_app.app_context():
        log("info", "Server booted up...")
        log("debug", "Latest autoupdate log:")
        log("debug", autoupdate_log)

